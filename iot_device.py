import time
import random
import threading
import paho.mqtt.client as mqtt

MQTT_BROKER = "localhost"
MQTT_PORT = 1883
MQTT_CLIENT_ID = "Device-2410010247"

NIM = "2410010247"
TOPIC_SUHU = f"iot/{NIM}/sensor/suhu"
TOPIC_RELAY = f"iot/{NIM}/aktuator/relay"
TOPIC_PWM = f"iot/{NIM}/aktuator/pwm"
TOPIC_STATUS_RELAY = f"iot/{NIM}/status/relay"

INTERVAL_KIRIM_DETIK = 3  # Sesuai tugas individu: tiap 3 detik

relay_state = "OFF"
pwm_value = 0

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("[MQTT] Terhubung ke broker")
        client.subscribe(TOPIC_RELAY, qos=0)
        client.subscribe(TOPIC_PWM, qos=0)
        print(f"[MQTT] Subscribe: {TOPIC_RELAY} & {TOPIC_PWM}")
    else:
        print(f"[MQTT] Gagal konek, kode: {rc}")

def on_message(client, userdata, msg):
    global relay_state, pwm_value
    pesan = msg.payload.decode("utf-8").strip()
    print(f"[MQTT] Masuk [{msg.topic}]: {pesan}")

    if msg.topic == TOPIC_RELAY:
        if pesan in ("ON", "1"):
            relay_state = "ON"
            print("[RELAY / GPIO 26] MENYALA (ON)")
        elif pesan in ("OFF", "0"):
            relay_state = "OFF"
            print("[RELAY / GPIO 26] MATI (OFF)")
        else:
            print(f"[RELAY] Perintah tidak dikenal: {pesan}")
            return
        client.publish(TOPIC_STATUS_RELAY, relay_state, qos=0)

    elif msg.topic == TOPIC_PWM:
        try:
            nilai = int(float(pesan))
            if 0 <= nilai <= 255:
                pwm_value = nilai
                print(f"[PWM / GPIO 2] Kecerahan LED diatur ke: {pwm_value}/255")
            else:
                print(f"[PWM] Nilai di luar 0-255: {nilai}")
        except ValueError:
            print(f"[PWM] Payload bukan angka: {pesan}")

def baca_suhu_simulasi():
    # Simulasi pembacaan suhu (jika pakai DHT22 asli di perangkat, ganti bagian ini)
    return round(random.uniform(25.0, 31.0), 2)

def loop_kirim_suhu(client):
    while True:
        suhu = baca_suhu_simulasi()
        client.publish(TOPIC_SUHU, str(suhu), qos=0)
        print(f"[SENSOR] Kirim suhu tiap 3s -> {TOPIC_SUHU}: {suhu} °C")
        time.sleep(INTERVAL_KIRIM_DETIK)

def main():
    client = mqtt.Client(client_id=MQTT_CLIENT_ID, protocol=mqtt.MQTTv311)
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(MQTT_BROKER, MQTT_PORT, keepalive=60)
    client.loop_start()
    time.sleep(1)

    thread_suhu = threading.Thread(target=loop_kirim_suhu, args=(client,), daemon=True)
    thread_suhu.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[STOP] Program dihentikan")
        client.loop_stop()
        client.disconnect()

if __name__ == "__main__":
    main()