const express = require('express'); //Trae la librería Express para poder crear un servidor web.
const xml2js = require('xml2js');  //Trae la librería para convertir entre XML y objetos JavaScript.
const app = express();  // Crea una instancia de servidor donde vamos a definir rutas y servicios

 //Usas encabezados (headers) y métodos de conversión para que el servidor sepa qué tipo de datos procesar o devolver.

app.use(express.json()); // Permite que el servidor entienda datos en formato JSON enviados por los clientes.
app.use(express.text({ type: 'application/xml' })); // Permite que el servidor entienda datos XML como texto plano.


// Datos simulados
//Creamos un arreglo en memoria con productos de ejemplo para probar las rutas JSON.
let productosJSON = [
  { id: 1, nombre: "Laptop", precio: 800 },
  { id: 2, nombre: "Mouse", precio: 20 }
];

let productosXML = [
  { id: 1, nombre: "Impresora", precio: 200 },
  { id: 2, nombre: "Teclado", precio: 30 }
];


// Funciones auxiliares
//Función que convierte un objeto de JavaScript en un XML, usando el nombre raíz que le indiquemos.
const toXML = (obj, rootName) => {
  const builder = new xml2js.Builder({ rootName });
  return builder.buildObject(obj);
};

//Función que convierte un XML recibido en un objeto JavaScript. Se usa async/await porque es asíncrona.
const fromXML = async (xml) => {
  const parser = new xml2js.Parser({ explicitArray: false });
  return await parser.parseStringPromise(xml);
};


// RUTAS JSON (CRUD completo)

app.get('/odata/json/productos', (req, res) => {
    res.setHeader('Content-Type', 'application/json');

    // Copiamos los productos para no modificar el arreglo original
    let resultado = [...productosJSON];

    // 
    if (req.query.$filter) {
        const [campo, operador, valor] = req.query.$filter.split(' ');
        if (operador === 'eq') {
            resultado = resultado.filter(p => String(p[campo]) === valor);
        }
    }

    // --- $orderby=campo desc|asc ---
    if (req.query.$orderby) {   //Verifica si el usuario envió el parámetro $orderby en la URL
        const [campo, direccion] = req.query.$orderby.split(' '); //Separa el nombre del campo y la dirección (asc o desc)
        resultado.sort((a, b) => {  //Ordena el arreglo de productos
            if (direccion === 'desc') return b[campo] - a[campo]; //Si es descendente, el mayor va primero
            return a[campo] - b[campo]; //Si es ascendente, el menor va primero
        });
    }

    res.send(JSON.stringify(resultado, null, 4));
});

app.post('/odata/json/productos', (req, res) => {
  const nuevo = { id: productosJSON.length + 1, ...req.body };
  productosJSON.push(nuevo);
  res.status(201).json(nuevo);
});

app.put('/odata/json/productos/:id', (req, res) => {
  const id = parseInt(req.params.id);
  const index = productosJSON.findIndex(p => p.id === id);
  if (index !== -1) {
    productosJSON[index] = { id, ...req.body };
    res.json(productosJSON[index]);
  } else {
    res.status(404).json({ error: "Producto no encontrado" });
  }
});

app.delete('/odata/json/productos/:id', (req, res) => {
  const id = parseInt(req.params.id);
  productosJSON = productosJSON.filter(p => p.id !== id);
  res.json({ mensaje: "Producto eliminado (JSON)" });
});

//  RUTAS XML (CRUD completo)

app.get('/odata/xml/productos', (req, res) => {
  let resultado = [...productosXML];

  // $filter simple
  if (req.query.$filter) {
    const [campo, operador, valor] = req.query.$filter.split(' ');
    if (operador === 'eq') {
      resultado = resultado.filter(p => String(p[campo]) === valor);
    }
  }

  // $orderby simple
  if (req.query.$orderby) {
    const [campo, direccion] = req.query.$orderby.split(' ');
    resultado.sort((a, b) => {
      if (direccion === 'desc') return b[campo] - a[campo];
      return a[campo] - b[campo];
    });
  }
  

  const xml = toXML({ producto: resultado }, 'productos');
  res.type('application/xml').send(xml);
});


app.post('/odata/xml/productos', async (req, res) => {
  const data = await fromXML(req.body);
  const nuevo = {
    id: productosXML.length + 1,
    nombre: data.producto.nombre,
    precio: parseFloat(data.producto.precio)
  };
  productosXML.push(nuevo);

  const xml = toXML(nuevo, 'producto');
  res.status(201).type('application/xml').send(xml);
});

app.put('/odata/xml/productos/:id', async (req, res) => {
  const id = parseInt(req.params.id);
  const index = productosXML.findIndex(p => p.id === id);
  if (index === -1) {
    const xml = toXML({ error: "Producto no encontrado" }, 'respuesta');
    return res.status(404).type('application/xml').send(xml);
  }

  const data = await fromXML(req.body);
  productosXML[index] = {
    id,
    nombre: data.producto.nombre,
    precio: parseFloat(data.producto.precio)
  };

  const xml = toXML(productosXML[index], 'producto');
  res.type('application/xml').send(xml);
});

app.delete('/odata/xml/productos/:id', (req, res) => {
  const id = parseInt(req.params.id);
  productosXML = productosXML.filter(p => p.id !== id);
  const xml = toXML({ mensaje: "Producto eliminado (XML)" }, 'respuesta');
  res.type('application/xml').send(xml);
});

//  Servidor
//Inicia el servidor en el puerto 3000. Muestra un mensaje en 
// consola indicando que el servidor está corriendo.
app.listen(3000, () => {
  console.log("Servidor OData con rutas separadas para JSON y XML corriendo en http://localhost:3000");
});