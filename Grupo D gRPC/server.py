import os
import sys

# CRÍTICO: Configurar encoding ANTES de importar psycopg2
if sys.platform == "win32":
    os.environ['PGCLIENTENCODING'] = 'UTF8'
    os.environ['PYTHONIOENCODING'] = 'utf-8'

from concurrent import futures
import grpc
import hello_pb2
import hello_pb2_grpc
from google.protobuf import empty_pb2
import psycopg2
from psycopg2 import pool
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '5432')
DB_NAME = os.getenv('DB_NAME', 'grpc_db')
DB_USER = os.getenv('DB_USER', 'grpc_user')
DB_PASS = os.getenv('DB_PASS', '12345')

connection_pool = None


class UserService(hello_pb2_grpc.UserServiceServicer):
    """Implementación del servicio UserService"""
    
    def _get_conn(self):
        """Obtener conexión del pool"""
        return connection_pool.getconn()
    
    def _put_conn(self, conn):
        """Devolver conexión al pool"""
        connection_pool.putconn(conn)
    
    def CreateUser(self, request, context):
        """Crear un nuevo usuario"""
        conn = self._get_conn()
        try:
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO users (name, email) VALUES (%s, %s) RETURNING id",
                (request.name, request.email)
            )
            new_id = cur.fetchone()[0]
            conn.commit()
            cur.close()
            return hello_pb2.UserReply(
                id=new_id,
                name=request.name,
                email=request.email,
                message="Usuario creado"
            )
        except Exception as e:
            conn.rollback()
            return hello_pb2.UserReply(message=f"Error: {e}")
        finally:
            self._put_conn(conn)
    
    def GetUser(self, request, context):
        """Obtener usuario por ID"""
        conn = self._get_conn()
        try:
            cur = conn.cursor()
            # Si request.id == 0 -> listar todos los usuarios
            if getattr(request, 'id', 0) == 0:
                cur.execute("SELECT id, name, email FROM users ORDER BY id")
                rows = cur.fetchall()
                cur.close()
                # Construir lista de usuarios como texto (JSON simple)
                try:
                    import json
                    users = [{"id": r[0], "name": r[1], "email": r[2]} for r in rows]
                    return hello_pb2.UserReply(message=json.dumps(users, ensure_ascii=False))
                except Exception:
                    # Fallback a representación simple si JSON falla
                    lines = [f"{r[0]}: {r[1]} <{r[2]}>" for r in rows]
                    return hello_pb2.UserReply(message='; '.join(lines))
            else:
                cur.execute("SELECT id, name, email FROM users WHERE id = %s", (request.id,))
                row = cur.fetchone()
                cur.close()

                if row:
                    return hello_pb2.UserReply(
                        id=row[0],
                        name=row[1],
                        email=row[2],
                        message="Usuario encontrado"
                    )
                else:
                    return hello_pb2.UserReply(message="Usuario no encontrado")
        except Exception as e:
            return hello_pb2.UserReply(message=f"Error: {e}")
        finally:
            self._put_conn(conn)

    def ListUsers(self, request, context):
        """Listar todos los usuarios (ListUsers RPC)"""
        conn = self._get_conn()
        try:
            cur = conn.cursor()
            cur.execute("SELECT id, name, email FROM users ORDER BY id")
            rows = cur.fetchall()
            cur.close()

            users = [hello_pb2.UserReply(id=r[0], name=r[1], email=r[2]) for r in rows]
            return hello_pb2.UsersList(users=users)
        except Exception as e:
            context.set_details(str(e))
            context.set_code(grpc.StatusCode.INTERNAL)
            return hello_pb2.UsersList()
        finally:
            self._put_conn(conn)
    
    def UpdateUser(self, request, context):
        """Actualizar usuario existente"""
        conn = self._get_conn()
        try:
            cur = conn.cursor()
            cur.execute(
                "UPDATE users SET name=%s, email=%s WHERE id=%s RETURNING id",
                (request.name, request.email, request.id)
            )
            row = cur.fetchone()
            conn.commit()
            cur.close()
            
            if row:
                return hello_pb2.UserReply(
                    id=row[0],
                    name=request.name,
                    email=request.email,
                    message="Usuario actualizado"
                )
            else:
                return hello_pb2.UserReply(message="Usuario no encontrado")
        except Exception as e:
            conn.rollback()
            return hello_pb2.UserReply(message=f"Error: {e}")
        finally:
            self._put_conn(conn)
    
    def DeleteUser(self, request, context):
        """Eliminar usuario"""
        conn = self._get_conn()
        try:
            cur = conn.cursor()
            cur.execute("DELETE FROM users WHERE id=%s RETURNING id", (request.id,))
            row = cur.fetchone()
            conn.commit()
            cur.close()
            
            if row:
                return hello_pb2.UserReply(id=row[0], message="Usuario eliminado")
            else:
                return hello_pb2.UserReply(message="Usuario no encontrado")
        except Exception as e:
            conn.rollback()
            return hello_pb2.UserReply(message=f"Error: {e}")
        finally:
            self._put_conn(conn)


def serve():
    """Iniciar el servidor gRPC"""
    global connection_pool
    
    db_config = {
        'host': DB_HOST,
        'port': DB_PORT,
        'database': DB_NAME,
        'user': DB_USER,
        'password': DB_PASS,
        'client_encoding': 'UTF8',
        'options': '-c client_encoding=UTF8'
    }
    
    print("Intentando conectar a PostgreSQL...")
    print(f"Host: {DB_HOST}, Database: {DB_NAME}, User: {DB_USER}")
    
    try:
        connection_pool = psycopg2.pool.SimpleConnectionPool(1, 10, **db_config)
        print("Pool de conexiones creado.")
    except Exception as e:
        print(f"Error al crear pool: {e}")
        raise
    
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    hello_pb2_grpc.add_UserServiceServicer_to_server(UserService(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    
    print("Servidor gRPC escuchando en :50051")
    
    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        print("Deteniendo servidor...")
    finally:
        if connection_pool:
            connection_pool.closeall()


if __name__ == '__main__':
    serve()
