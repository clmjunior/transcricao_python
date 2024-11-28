import time
import requests

# Simulação de classes e funções equivalentes ao Arduino
class Servo:
    def __init__(self):
        self.position = 0

    def write(self, position):
        self.position = position
        print(f"Servo na posição {position}")

class LCD:
    def __init__(self):
        self.lines = ["", ""]

    def print(self, message, line=0):
        self.lines[line] = message
        self.display()

    def clear(self):
        self.lines = ["", ""]
        self.display()

    def set_cursor(self, col, line):
        pass  # Não necessário para esta simulação

    def display(self):
        print("\n".join(self.lines))

class Keypad:
    def __init__(self, keys):
        self.keys = keys

    def get_key(self):
        return input("Digite uma tecla (ou pressione Enter para pular): ").strip()

# Configurações iniciais
myservo = Servo()
lcd = LCD()
CPF_LENGTH = 11  # Sem NULL char, pois strings em Python não precisam disso

door = True
data = ""  # Para armazenar o CPF
open_time = 0
auto_close_delay = 5  # Segundos
API_URL = "http://localhost:3000/api/validate_cpf"

def servo_open():
    for pos in range(180, -1, -5):
        myservo.write(pos)
        time.sleep(0.015)
    global open_time
    open_time = time.time()

def servo_close():
    for pos in range(0, 181, 5):
        myservo.write(pos)
        time.sleep(0.015)

def clear_data():
    global data
    data = ""

def validate_cpf(cpf):
    try:
        response = requests.post(API_URL, json={"cpf": cpf})
        if response.status_code == 200:
            result = response.json()
            return result.get("authorized", False)
        else:
            lcd.print("Erro na API", line=1)
            return False
    except requests.RequestException as e:
        print(f"Erro ao consultar API: {e}")
        lcd.print("Erro API", line=1)
        return False

def open_catraca():
    global data, door
    lcd.print("  Digite CPF  ", line=0)
    keypad = Keypad(keys=None)  # Não estamos simulando o teclado real aqui

    while True:
        custom_key = keypad.get_key()
        if custom_key:
            if custom_key == "*":  # Finaliza a entrada do CPF
                if len(data) == CPF_LENGTH:
                    lcd.clear()
                    lcd.print("Validando CPF...", line=0)
                    if validate_cpf(data):
                        servo_open()
                        lcd.print("Acesso Permitido", line=1)
                        door = False
                        break
                    else:
                        lcd.clear()
                        lcd.print("CPF Invalido", line=1)
                        time.sleep(1)
                        door = True
                        break
                else:
                    lcd.clear()
                    lcd.print("CPF Incompleto", line=1)
                    time.sleep(1)
            else:
                if len(data) < CPF_LENGTH:
                    data += custom_key
                    lcd.print(data, line=1)
                else:
                    lcd.print("CPF Cheio", line=1)
                    time.sleep(1)

def main():
    global door, open_time
    servo_close()
    lcd.print("   Catraca   ", line=0)
    lcd.print("--Aguardando--", line=1)
    time.sleep(3)
    lcd.clear()

    while True:
        if not door:
            if time.time() - open_time >= auto_close_delay:
                servo_close()
                lcd.clear()
                lcd.print("Catraca Fechada", line=0)
                time.sleep(3)
                door = True
                open_time = 0
        else:
            open_catraca()

if __name__ == "__main__":
    main()
