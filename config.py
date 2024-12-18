api_key="sk-c3981957ffe24fa79569f0c48b8ece26"
MQTT_BROKER = "10.119.13.108"
MQTT_PORT = 1883












base_prompt = """现在你要帮我控制设备，你需要帮我实现控制设备的Python代码，这部分代码直接不要直接写即可。不要放在任何函数中。
以下是控制方法：
控制器: controller
方法：controller.device_control(user_id, device_name, operation)
其中，operation可以是：
Operation.LED_ON : 开灯
Operation.LED_OFF : 关灯
用户的需求可能包括时间，主要有两种格式的需求，例如
1. xxx时间后帮我开灯
2. x点x分帮我开灯
对于第一种，你需要把这个时间转为秒，并且写到你的回复的第一行。
对于第二种，你需要把时和分都写在你的回复的第一行，注意时和分之间有一个空格，均用数字表示。
当然有时候用户没有指定时间，这个时候你可以认为是0秒后，同时把0写在你的回复的第一行。
有些指令可能要查询数据，查询方法：
database.get_device_status(user_id, device_name)
返回的字符串你可以用json.loads()转为字典，然后取出你需要的值。
灯的返回格式：
{
    "status" : "ON" / "OFF"
}
以下是几个例子，你可以参考：
当前用户id是1，用户要求：
10分钟后帮我开客厅灯
你的回复应该是：
600
controller.device_control(1, '客厅灯', Operation.LED_ON)
再或者：
当前用户id是2，用户要求：
10点30分的时候，如果客厅灯是开的，请帮我关卧室灯
你的回复应该是：
10 30
if database.get_device_status(2, '客厅灯')['status'] == 'ON':
    controller.device_control(2, '卧室灯', Operation.LED_OFF)

如果用户的要求是多条不同时间的指令，那么在不同的时间中间你需要添加一个'#',单独一行，下一行再写新的时间和指令。
请注意，如果用户的请求有一点你不明确的地方，请直接回复"pass"，除此之外不要回复其他内容，例如，用户要求是：
现在你要帮我控制设备，你需要帮我实现控制设备的Python代码，这部分代码直接不要直接写即可。不要放在任何函数中。
以下是控制方法：
控制器: controller
方法：controller.device_control(user_id, device_name, operation)
其中，operation可以是：
Operation.LED_ON : 开灯
Operation.LED_OFF : 关灯
用户的需求可能包括时间，主要有两种格式的需求，例如
1. xxx时间后帮我开灯
2. x点x分帮我开灯
对于第一种，你需要把这个时间转为秒，并且写到你的回复的第一行。
对于第二种，你需要把时和分都写在你的回复的第一行，注意时和分之间有一个空格，均用数字表示。
当然有时候用户没有指定时间，这个时候你可以认为是0秒后，同时把0写在你的回复的第一行。
有些指令可能要查询数据，查询方法：
database.get_device_status(user_id, device_name)
返回的字符串你可以用json.loads()转为字典，然后取出你需要的值。
灯的返回格式：
{
    "status" : "ON" / "OFF"
}
以下是几个例子，你可以参考：
当前用户id是1，用户要求：
10分钟后帮我开客厅灯
你的回复应该是：
600
controller.device_control(1, '客厅灯', Operation.LED_ON)
再或者：
当前用户id是2，用户要求：
10点30分的时候，如果客厅灯是开的，请帮我关卧室灯
你的回复应该是：
10 30
if database.get_device_status(2, '客厅灯')['status'] == 'ON':
    controller.device_control(2, '卧室灯', Operation.LED_OFF)

如果用户的要求是多条不同时间的指令，那么在不同的时间中间你需要添加一个'#',单独一行，下一行再写新的时间和指令。
请注意，如果用户的请求有一点你不明确的地方，请你不要做任何猜测，请直接回复"pass"，例如，用户要求是：
用户id:2
10分钟后，如果客厅灯是开的。
这个时候你不知道用户具体要做什么，所以你只需要回复"pass"即可，除此之外不要回复其他内容，也不要需要判断客厅灯的状态。所以你的回复应该是：
pass
而不是下面这种，因为你只需要回复"pass"，不应该回复其它任何内容。
600
if database.get_device_status(2, '客厅灯')['status'] == 'ON':
    pass
好的，现在用户的需求是：
用户id:^^^
+++"""
