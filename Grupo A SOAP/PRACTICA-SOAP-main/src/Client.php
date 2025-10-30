<?php
// Ejemplo de cliente SOAP usando el WSDL del servicio
$wsdl = __DIR__ . '/service.wsdl';
$cliente = new SoapClient($wsdl, [
    'trace' => 1
]);

echo "<h3> Lista de clientes:</h3>";
print_r($cliente->listarClientes());

echo "<h3> Cliente con ID 1:</h3>";
print_r($cliente->obtenerCliente(1));

echo "<h3> Agregando nuevo cliente:</h3>";
echo $cliente->agregarCliente("José", "jose@example.com");
