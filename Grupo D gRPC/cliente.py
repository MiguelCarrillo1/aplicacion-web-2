import grpc
import hello_pb2
from google.protobuf import empty_pb2
import hello_pb2_grpc

SERVER = 'localhost:50051'


def run():
    """Ejecutar cliente interactivo"""
    channel = grpc.insecure_channel(SERVER)
    stub = hello_pb2_grpc.UserServiceStub(channel)
    while True:
        print("\n=== Menú CRUD ===")
        print("1. Crear usuario")
        print("2. Buscar usuario por ID")
        print("3. Listar todos los usuarios")
        print("4. Actualizar usuario")
        print("5. Eliminar usuario")
        print("6. Salir")

        opc = input("Elige una opción: ").strip()

        if opc == '1':
            name = input('Nombre: ')
            email = input('Email: ')
            try:
                resp = stub.CreateUser(hello_pb2.UserRequest(name=name, email=email))
                if resp.message == "Usuario creado":
                    print(f'✓ Usuario creado exitosamente - ID: {resp.id}')
                else:
                    print(f'✗ {resp.message}')
            except Exception as e:
                print(f'✗ Error: {e}')

        elif opc == '2':
            try:
                id_ = int(input('ID: '))
                resp = stub.GetUser(hello_pb2.UserIdRequest(id=id_))
                if getattr(resp, 'id', 0) and resp.id > 0:
                    print(f'✓ Usuario encontrado:')
                    print(f'  ID: {resp.id}')
                    print(f'  Nombre: {resp.name}')
                    print(f'  Email: {resp.email}')
                else:
                    print(f'✗ {resp.message}')
            except ValueError:
                print('✗ Error: Debes ingresar un número válido')
            except Exception as e:
                print(f'✗ Error: {e}')

        elif opc == '3':
            try:
                resp = stub.ListUsers(empty_pb2.Empty())
                if getattr(resp, 'users', None) and len(resp.users) > 0:
                    print('\u2713 Usuarios encontrados:')
                    for u in resp.users:
                        print(f"  ID: {u.id}  Nombre: {u.name}  Email: {u.email}")
                else:
                    print('\u2717 No hay usuarios registrados')
            except Exception as e:
                print(f'\u2717 Error: {e}')

        elif opc == '4':
            try:
                id_ = int(input('ID: '))
                name = input('Nuevo nombre: ')
                email = input('Nuevo email: ')
                resp = stub.UpdateUser(hello_pb2.UserRequest(id=id_, name=name, email=email))
                if resp.message == "Usuario actualizado":
                    print(f'✓ Usuario actualizado exitosamente')
                else:
                    print(f'✗ {resp.message}')
            except ValueError:
                print('✗ Error: Debes ingresar un número válido')
            except Exception as e:
                print(f'✗ Error: {e}')

        elif opc == '5':
            try:
                id_ = int(input('ID a eliminar: '))
                resp = stub.DeleteUser(hello_pb2.UserIdRequest(id=id_))
                if resp.message == "Usuario eliminado":
                    print(f'✓ Usuario eliminado exitosamente')
                else:
                    print(f'✗ {resp.message}')
            except ValueError:
                print('✗ Error: Debes ingresar un número válido')
            except Exception as e:
                print(f'✗ Error: {e}')

        elif opc == '6':
            print("¡Hasta luego!")
            break

        else:
            print('✗ Opción no válida')


if __name__ == '__main__':
    run()
