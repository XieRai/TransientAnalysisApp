#include <BLEDevice.h>
#include <BLEServer.h>
#include <BLEUtils.h>
#include <BLE2902.h>

// UUID yang digunakan webapp
#define SERVICE_UUID        "0000ffe0-0000-1000-8000-00805f9b34fb"
#define CHARACTERISTIC_UUID "0000ffe1-0000-1000-8000-00805f9b34fb"

const int adcPin = 34;
const float adcReferenceVoltage = 3.3;
const int adcMaxValue = 4095;

BLECharacteristic* characteristic;
uint32_t sequenceNumber = 0;

void setup() {
  Serial.begin(115200);
  analogReadResolution(12);

  BLEDevice::init("RLC-ESP32");

  BLEServer* server = BLEDevice::createServer();
  BLEService* service = server->createService(SERVICE_UUID);

  characteristic = service->createCharacteristic(
    CHARACTERISTIC_UUID,
    BLECharacteristic::PROPERTY_READ |
    BLECharacteristic::PROPERTY_NOTIFY
  );
  characteristic->addDescriptor(new BLE2902());

  service->start();
  BLEAdvertising* advertising = BLEDevice::getAdvertising();
  advertising->addServiceUUID(SERVICE_UUID);
  advertising->start();

  Serial.println("BLE aktif. Hubungkan dari webapp.");
}

void loop() {
  const int adcValue = analogRead(adcPin);
  const float voltage = adcValue * adcReferenceVoltage / adcMaxValue;

  char payload[128];
  snprintf(
    payload,
    sizeof(payload),
    "{\"voltage\":%.3f,\"current\":0,\"sequence\":%lu,\"device_id\":\"rlc-01\"}\n",
    voltage,
    (unsigned long)sequenceNumber++
  );

  characteristic->setValue((uint8_t*)payload, strlen(payload));
  characteristic->notify();

  Serial.print("ADC: ");
  Serial.print(adcValue);
  Serial.print("  Voltage: ");
  Serial.println(voltage, 3);

  delay(10);
}