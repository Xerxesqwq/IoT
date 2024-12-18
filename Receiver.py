from utils import MQTTReceiver

receiver = MQTTReceiver()
receiver.client.loop_forever()