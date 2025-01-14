#include <WiFi.h>
#include <PubSubClient.h>
#include "DHT.h"
#define DHTTYPE DHT11   // DHT 11
#define DHTPIN 4     // Digital pin connected to the DHT sensor
#define WIFI_AP "ZJUWLAN-Secure"
#define WIFI_PASSWORD "ZJU_is_Great"
char MqttServer[] = "10.119.13.108";
WiFiClient Client;
PubSubClient client(Client);

unsigned long lastSend;
//定义风扇端口
const int motorIn1 = 25;   
const int motorIn2 = 26;

#define Speed_0 0
#define Speed_1 185
#define Speed_2 255
int Speed_now = 0;

String sub_topic;
String pub_topic;
int device_id = 6;

DHT dht(DHTPIN, DHTTYPE);

void setup() {
  Serial.begin(9600); 
  pub_topic = "devices/control/" + String(device_id);
  sub_topic = "devices/public/" + String(device_id);
  client.setKeepAlive(15);
  InitWiFi();         // 连接WiFi
  client.setServer(MqttServer, 1883); // 连接WiFi之后，连接MQTT服务器
  lastSend = 0;
  client.setCallback(receiveCallback);
}

void loop() {
  //put your main code here, to run repeatedly:
  if (WiFi.status()!= WL_CONNECTED) {
    while (WiFi.status()!= WL_CONNECTED) {
      Serial.print("[loop()]Attempting to connect to WPA SSID: ");
      Serial.println(WIFI_AP);
      delay(2000);
    }
    Serial.println("[loop()]Connected to AP");
  }
  if ( !client.connected() ) {
    reconnect();
  }
  if( millis() - lastSend > 5000){
    sendData();
    lastSend = millis();
  }
  client.loop();
}


void InitWiFi(){
// 初始化软串口
Serial.begin(9600);
WiFi.mode(WIFI_STA);//关闭STA模式下wifi休眠，提高响应速度
WiFi.setSleep(false);// 断开之前的连接
WiFi.disconnect(true);// attempt to connect to WiFi network
Serial.print("[InitWiFi]Attempting to connect to WPA SSID: ");
Serial.println(WIFI_AP);
WiFi.begin(WIFI_AP, WIFI_PASSWORD);// 尝试连接WiFi网络

while (WiFi.status() != WL_CONNECTED) {
  Serial.print("[InitWiFi]Attempting to connect to WPA SSID: ");
  Serial.println(WIFI_AP);
  delay(2000);
}
  Serial.println("[InitWiFi]Connected to AP");
}

void sendFanSpeed(int speed){
  Speed_now = speed;
  dacWrite(motorIn1, speed);  // 高电平
  dacWrite(motorIn2, 0);    // 低电平
  Serial.print("Fan speed set to:");
  Serial.print(speed);
}

//从这里开始每10S传送一次温度数据给服务端
void sendData()
{
  String payload;
  switch(Speed_now){
    case 0:
      payload = "OFF";
      break;
    case 185:
      payload = "LV1";
      break;
    case 255:
      payload = "LV2";
      break;
  }
  Serial.println(payload);
  //dht.readTemperature(); 
  char attributes[10];
  payload.toCharArray( attributes, 10 );
  client.publish(sub_topic.c_str(), attributes);
}


//从MQTT服务器上订阅主题
void reconnect() {
// Loop until we're reconnected
  while (!client.connected()) {
    Serial.print("[reconnect]Connecting to MQTT Server ...");
    String clientId = "ESP8266Client-"; 
    clientId += String(random(0xffff), HEX); //产生一个随机数字 以免多块板子重名
// Attempt to connect
    if (client.connect(clientId.c_str(), NULL, NULL)) {
      Serial.println("[DONE]");
      subscribeTopic();
    } else {
      Serial.print("[FAILED] [ mqtt connect error code = ]");
      Serial.print(client.state());
      Serial.println(" : retry again in 5 seconds");// Wait 5 seconds before retrying
      delay(5000);
    }
  }
}

// 订阅指定主题
void subscribeTopic(){
//这么做是为确保不同设备使用同一个MQTT服务器测试消息订阅时，所订阅的主题名称不同
  String topicString = pub_topic;
  char subTopic[topicString.length() + 1];
  strcpy(subTopic, topicString.c_str());
//通过串口监视器输出是否成功订阅主题以及订阅的主题名称
  if(client.subscribe(subTopic)){
    Serial.print('\n');
    Serial.println("Subscrib Topic:");
    Serial.println(subTopic);
  } else {
    Serial.print("Subscribe Fail...");
  } 
}

// 收到信息后的回调函数
void receiveCallback(char* topic, byte* payload, unsigned int length) {
  Serial.print("Message Received [");
  Serial.print(topic);
  Serial.print("] ");
  char message[length + 1];
  for (unsigned int i = 0; i < length; i++) {
    message[i] = (char)payload[i];
  }
  message[length] = '\0';  // 添加字符串结束符
  String payload1;
  payload1 = String(message);
  Serial.print(payload1);
  if(payload1 =="OFF"){
    sendFanSpeed(Speed_0);
    Serial.println("关闭风扇");
  }
  else if(payload1=="LV1"){
    sendFanSpeed(Speed_2);
    delay(3500);
    sendFanSpeed(Speed_1);
    Serial.println("开启挡位1");
  }
  else if(payload1=="LV2"){
    sendFanSpeed(Speed_2);
    Serial.println("开启挡位2");
  }
  else{
    Serial.print("输入有误");
  }
  sendData();
}