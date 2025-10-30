<?php
require_once __DIR__ . '/../vendor/autoload.php';

use Src\Database;

class ClienteService {
    private $conn;

    public function __construct() {
        $db = new Database();
        $this->conn = $db->getConnection();
    }

    public function listarClientes() {
        $sql = "SELECT * FROM clientes ORDER BY id";
        $stmt = $this->conn->query($sql);
        return $stmt->fetchAll(PDO::FETCH_ASSOC);
    }

    public function obtenerCliente($id) {
        $sql = "SELECT * FROM clientes WHERE id = :id";
        $stmt = $this->conn->prepare($sql);
        $stmt->execute(['id' => $id]);
        $cliente = $stmt->fetch(PDO::FETCH_ASSOC);
        return $cliente ?: ["error" => "Cliente no encontrado"];
    }

    public function agregarCliente($nombre, $correo) {
        $sql = "INSERT INTO clientes (nombre, correo) VALUES (:nombre, :correo)";
        $stmt = $this->conn->prepare($sql);
        $stmt->execute(['nombre' => $nombre, 'correo' => $correo]);
        return "Cliente agregado correctamente";
    }

    public function actualizarCliente($id, $nombre, $correo) {
        $sql = "UPDATE clientes SET nombre = :nombre, correo = :correo WHERE id = :id";
        $stmt = $this->conn->prepare($sql);
        $stmt->execute(['id' => $id, 'nombre' => $nombre, 'correo' => $correo]);
        return "Cliente actualizado correctamente";
    }

    public function eliminarCliente($id) {
        $sql = "DELETE FROM clientes WHERE id = :id";
        $stmt = $this->conn->prepare($sql);
        $stmt->execute(['id' => $id]);
        return "Cliente eliminado correctamente";
    }
}

$wsdlPath = __DIR__ . '/service.wsdl';
$server = new SoapServer($wsdlPath);
$server->setClass('ClienteService');
$server->handle();
