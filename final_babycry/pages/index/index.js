import mqtt from'../../utils/mqtt.js';
const aliyunOpt = require('../../utils/aliyun/aliyun_connect');
let that = null;
Page({
    data:{
      emotionImage:"",
      //设置温度值和湿度值 
      detect:0,
      emotion:"",
      // humidity:"",

      client:null,//记录重连的次数
      reconnectCounts:0,//MQTT连接的配置
      options:{
        protocolVersion: 4, //MQTT连接协议版本
        clean: false,
        reconnectPeriod: 1000, //1000毫秒，两次重新连接之间的间隔
        connectTimeout: 30 * 1000, //1000毫秒，两次重新连接之间的间隔
        resubscribe: true, //如果连接断开并重新连接，则会再次自动订阅已订阅的主题（默认true）
        clientId: '',
        password: '',
        username: '',
      },

      aliyunInfo: {
        productKey: 'k022e8OSwlm', //阿里云连接的三元组 ，请自己替代为自己的产品信息!!
        deviceName: 'app_dev', //阿里云连接的三元组 ，请自己替代为自己的产品信息!!
        deviceSecret: '7aed6b2d4229569ecf2d01b6e8d34168', //阿里云连接的三元组 ，请自己替代为自己的产品信息!!
        regionId: 'cn-shanghai', //阿里云连接的三元组 ，请自己替代为自己的产品信息!!
        pubTopic: '/sys/k022e8OSwlm/app_dev/thing/event/property/post', //发布消息的主题
        subTopic: '/sys/k022e8OSwlm/raspi_dev/thing/service/property/set', //订阅消息的主题
      },
    },

  onLoad:function(){
    const self = this;
    that = this;
    let clientOpt = aliyunOpt.getAliyunIotMqttClient({
      productKey: that.data.aliyunInfo.productKey,
      deviceName: that.data.aliyunInfo.deviceName,
      deviceSecret: that.data.aliyunInfo.deviceSecret,
      regionId: that.data.aliyunInfo.regionId,
      port: that.data.aliyunInfo.port,
    });

    console.log("get data:" + JSON.stringify(clientOpt));
    let host = 'wxs://' + clientOpt.host;
    
    this.setData({
      'options.clientId': clientOpt.clientId,
      'options.password': clientOpt.password,
      'options.username': clientOpt.username,
    })
    console.log("this.data.options host:" + host);
    console.log("this.data.options data:" + JSON.stringify(this.data.options));

    //访问服务器
    this.data.client = mqtt.connect(host, this.data.options);

    this.data.client.on('connect', function (connack) {
      wx.showToast({
        title: '连接成功'
      })
      console.log("连接成功");
    })

    //接收消息监听
    this.data.client.on("message", function (topic, payload) {
      console.log(" 收到 topic:" + topic + " , payload :" + payload);
      if (topic === "/sys/k022e8OSwlm/app_dev/thing/service/property/set"){
      // 解析收到的消息
      const messageData = JSON.parse(payload);
      console.log("解析后的消息内容:", messageData);
      const testValue = messageData.items.emotion.value;
      console.log("收到的 emotion 值:", testValue);
      //更新界面数据
      self.setData({
        emotion: testValue,
      }, function () {
        console.log("界面数据更新成功:", this.data.emotion);
          // 在界面数据更新成功后显示弹窗提醒
        wx.showToast({
          title: '检测完成',
          icon: 'success',
          duration: 1000,
        });
          // 根据不同的标签值设置对应的图片路径
        switch (this.data.emotion) {
          case '宝宝醒了':
            this.setData({
              emotionImage: 'images/awake.png', // 设置醒了的照片路径
            });
            break;
          case '宝宝饿了':
            this.setData({
              emotionImage: 'images/hungry.png', // 设置饿了的照片路径
            });
            break;
          case '宝宝想要拥抱':
            this.setData({
              emotionImage: 'images/hug.png', // 设置想要拥抱的照片路径
            });
            break;
          case '宝宝心情不好':
            this.setData({
              emotionImage: 'images/diaper.png', // 设置心情不好的照片路径
            });
            break;
          default:
            this.setData({
              emotionImage: '', // 如果标签值不匹配任何情况，可以设置一个默认图片路径或为空
            });
        }
      });
    }
    })

    //服务器连接异常的回调
    that.data.client.on("error", function (error) {
      console.log(" 服务器 error 的回调" + error)

    })
    //服务器重连连接异常的回调
    that.data.client.on("reconnect", function () {
      console.log(" 服务器 reconnect的回调")

    })
    //服务器连接异常的回调
    that.data.client.on("offline", function (errr) {
      console.log(" 服务器offline的回调")
    })
  },
  onClickOpen() {
    that.sendCommond(0);
  },
  sendCommond(cmd) {
    // let sendData = {
    //   //detect: cmd,
      
    // };
    let sendData = 
    {
    
      "id": 1691332722998,
      "params": {"detect": 1},
      "version": "1.0",
      "method": "thing.event.property.post"
    
  };
    //发布消息
    if (this.data.client && this.data.client.connected) {
      this.data.client.publish(this.data.aliyunInfo.pubTopic, JSON.stringify(sendData));
      console.log("************************")
      console.log(this.data.aliyunInfo.pubTopic)
      console.log(JSON.stringify(sendData))
    } else {
      wx.showToast({
        title: '请先连接服务器',
        icon: 'none',
        duration: 2000
      })
    }
  }
})