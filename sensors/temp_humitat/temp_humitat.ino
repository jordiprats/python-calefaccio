#include <ESP8266WiFi.h>
#include <PubSubClient.h>
#include "DHTesp.h"

#define WIFI_SSID "WIFI"
#define WIFI_PASSWORD "password"
#define MQTT_SERVER "1.2.3.4"
#define MQTT_USERNAME "sensor"
#define MQTT_PASSWORD "password"
#define TEMPERATURE_TOPIC "room2/temperature"
#define HUMIDITY_TOPIC "room2/humidity"
#define COMFORT_TOPIC "room2/comfort"

/** Initialize DHT sensor */
DHTesp dht;
/** Pin number for DHT11 data pin */
int dhtPin = 17;
/** Comfort profile */
ComfortState cf;

WiFiClient espClient;
PubSubClient client(espClient);

void setup_wifi()
{
  delay(10);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  while (WiFi.status() != WL_CONNECTED)
  {
    delay(1000);
  }
}

void setup()
{
  setup_wifi();
  client.setServer(MQTT_SERVER, 1883);
  dht.setup(17, DHTesp::DHT11); // Connect DHT sensor to GPIO 17
}

void reconnect() 
{
  // Loop until we're reconnected
  while (!client.connected())
  {
    // Attempt to connect
    // If you do not want to use a username and password, change next line to
    // if (client.connect("ESP8266Client")) {
    if (!client.connect("ESP8266Client", MQTT_USERNAME, MQTT_PASSWORD))
    {
      // Wait 5 seconds before retrying
      delay(5000);
    }
  }
}

void loop()
{
  if (!client.connected())
  {
    reconnect();
  }
  client.loop();
  
  delay(dht.getMinimumSamplingPeriod());

  float temperature = dht.getTemperature();
  float humidity = dht.getHumidity();
  float cr = dht.getComfortRatio(cf, temperature, humidity);

  client.publish(TEMPERATURE_TOPIC, String(temperature).c_str(), true);
  client.publish(HUMIDITY_TOPIC, String(humidity).c_str(), true);
  switch(cf)
  {
    case Comfort_OK:
      client.publish(COMFORT_TOPIC, "OK", true);
      break;
    case Comfort_TooHot:
      client.publish(COMFORT_TOPIC, "Too hot", true);
      break;
    case Comfort_TooCold:
      client.publish(COMFORT_TOPIC, "Too cold", true);
      break;
    case Comfort_TooDry:
      client.publish(COMFORT_TOPIC, "Too dry", true);
      break;
    case Comfort_TooHumid:
      client.publish(COMFORT_TOPIC, "Too humid", true);
      break;
    case Comfort_HotAndHumid:
      client.publish(COMFORT_TOPIC, "Too hot and too humid", true);
      break;
    case Comfort_HotAndDry:
      client.publish(COMFORT_TOPIC, "Too hot and dry", true);
      break;
    case Comfort_ColdAndHumid:
      client.publish(COMFORT_TOPIC, "Too cold and humid", true);
      break;
    case Comfort_ColdAndDry:
      client.publish(COMFORT_TOPIC, "Too cold and dry", true);
      break;
    default:
      client.publish(COMFORT_TOPIC, "unknown", true);
      break;
  };
  delay(600000); //wait 10 minute
}
