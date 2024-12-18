api_key="sk-c3981957ffe24fa79569f0c48b8ece26"
MQTT_BROKER = "10.119.13.108"
MQTT_PORT = 1883












base_prompt = """### 控制设备的Python代码生成

**任务描述**:
你需要生成控制设备的Python代码，根据用户的需求来安排设备的操作时间，并且不要将代码放在任何函数中。

**控制方法**:
- 控制器: `controller`
- 1.方法: `controller.device_control(user_id, device_name, operation)`
  - `operation` 可以是:
    - `Operation.LED_ON` : 开灯
    - `Operation.LED_OFF` : 关灯
- 2.方法: `controller.device_control_all(user_id, type, operation)`
    - `type` 可以是: "LED" 或 "AIR_CONDITIONER", 所有和灯相关的设备都是LED（例如灯，light），所有和空调相关的设备都是AIR_CONDITIONER。
    - 该方法会控制所有该类型的设备。

**时间处理**:
- 用户需求可能包含时间，主要有两种格式:
  1. "xxx时间后帮我开灯" (例如: "10分钟后帮我开灯")
     - 将时间转换为秒，并将其写在回复的第一行。
  2. "x点x分帮我开灯" (例如: "10点30分帮我开灯")
     - 将小时和分钟写在回复的第一行，用空格分隔，均用数字表示。
- 如果用户没有指定时间，默认为0秒，并将0写在回复的第一行。

**数据查询**:
- 有些指令需要先查询设备状态，查询方法:
  - `database.get_device_status(user_id, device_name)`
  - 返回的字符串可以用 `json.loads()` 转为字典，取出需要的值。
- 灯的状态返回格式:
  ```json
  {
    "status" : "ON" / "OFF"
  }
  ```

**多条指令处理**:
- 如果用户的要求包含多条不同时间的指令，在不同的时间中间添加一个单独的 `#` 行，下一行再写新的时间和指令。

**不明确请求处理**:
- 如果用户的请求有任何不明确的地方，请直接回复 "pass"，除此之外不要回复其他内容。

**示例**:

1. 当前用户id是1，用户要求:
   - "10分钟后帮我开客厅灯"
   - 回复:
     ```
     600
     controller.device_control(1, '客厅灯', Operation.LED_ON)
     ```

2. 当前用户id是2，用户要求:
   - "10点30分的时候，如果客厅灯是开的，请帮我关卧室灯"
   - 回复:
     ```
     10 30
     if database.get_device_status(2, '客厅灯')['status'] == 'ON':
         controller.device_control(2, '卧室灯', Operation.LED_OFF)
     ```

3. 如果用户的要求有多条不同时间的指令，例如:
   - "5分钟后开客厅灯，10分钟后关卧室灯"
   - 回复:
     ```
     300
     controller.device_control(1, '客厅灯', Operation.LED_ON)
     #
     600
     controller.device_control(1, '卧室灯', Operation.LED_OFF)
     ```

4. 如果用户的请求不明确，例如:
   - "10分钟后，如果客厅灯是开的。"
   - 回复:
     ```
     pass
     ```
---

**注意**: 请严格按照上述要求生成代码，并确保代码不放在任何函数中，回复无需markdown格式。
现在用户的需求是：
用户id:^^^
+++"""
