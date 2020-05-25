# -*- coding: utf-8 -*-
from flask import request, jsonify, Blueprint
from common.libs.tools import get_current_time, get_md5, return_data, get_code
import uuid, json
import requests
from common.models import User, Admin
from application import db
from sqlalchemy import text
import datetime

index_page = Blueprint("index", __name__)


@index_page.route("/getInfos", methods=["POST"])
def getInfos():
    '''
    发起预支付
    '''
    now = str(datetime.datetime.now())
    idx = now.index(".")
    create_time = now[0:idx]

    params = request.json
    pay_way = "alipay" if params.get("type") == "1" else "wechat"
    app_secret = "a2e81f680103f8787fbce8d9ed1dc4df"
    pay_infos = {
        "app_id": "21364048",
        "out_order_sn": get_code(),
        "name": "内容付费产品",
        "pay_way": pay_way,
        "price": params.get("price") * 100,  # 单位为分
        "attach": "商家的自定义字段，支付回调会原路返回",
        "notify_url": "http://127.0.0.1:5000/index/getPayState",
    }
    generate_key = pay_infos.get("app_id") + pay_infos.get("out_order_sn") + pay_infos.get("name") + \
                   pay_infos.get("pay_way") + str(pay_infos.get("price")) + pay_infos.get("attach") + pay_infos.get(
        "notify_url") + app_secret

    sign = get_md5(generate_key)
    pay_infos["sign"] = sign
    headers = {'content-type': 'application/x-www-form-urlencoded'}
    # 1. 生成系统订单，存入数据库
    user = User(params.get("domain"), params.get("phone"), pay_infos.get("out_order_sn"), create_time)
    db.session.add(user)
    db.session.commit()
    # 2. 发起预支付，获取支付二维码
    result = requests.post("https://open.yunmianqian.com/api/pay", data=pay_infos, headers=headers)
    result_data = json.loads(result.text)
    if result_data.get("code") == 200:
        # 成功调用
        data = result_data.get("data")
        return jsonify(return_data("调用成功", data))
    elif result_data.get("code") == 1001:
        # 签名错误
        return jsonify(return_data("签名错误"))
    elif result_data.get("code") == 1002:
        # 无可用二维码
        return jsonify(return_data("无可用二维码"))
    elif result_data.get("code") == 1003:
        # 缺少参数
        return jsonify(return_data("缺少参数"))
    elif result_data.get("code") == 1004:
        # 请求值错误
        return jsonify(return_data("请求值错误"))

    return "hello world"


@index_page.route("/getPayState", methods=["POST"])
def getPayState():
    '''
    云端支付完成后的回调通知
    '''
    forms = request.form
    merchant_order_number = forms.get("out_order_sn")
    result = User.query.filter_by(merchant_order_number=merchant_order_number).first()
    result.pay_time = forms.get("paid_at")
    result.pay_type = forms.get("pay_way")
    result.qr_price = int(forms.get("qr_price")) / 100
    result.pay_price = int(forms.get("pay_price")) / 100
    result.cloud_order_number = forms.get("order_sn")
    if forms.get("qr_type") == "fixed":
        qr_type = '个人版固额二维码'
    elif forms.get("qr_type") == "no_fixed":
        qr_type = '个人版非固额二维码'
    elif forms.get("qr_type") == "business":
        qr_type = '商业版收款码'
    elif forms.get("qr_type") == "original":
        qr_type = '原价'
    result.qr_type = qr_type
    db.session.commit()
    return "success"


@index_page.route("/getOder", methods=["POST"])
def getOder():
    '''
    获取订单状态
    '''
    params = request.json
    result = User.query.filter_by(merchant_order_number=params.get("order")).first()

    if result.pay_time is not None:
        # 订单支付成功
        data = {
            "cloud_order_num": result.cloud_order_number,
            "pay_price": result.pay_price,
            "pay_time": result.pay_time,
            "pay_type": result.pay_type
        }
        return jsonify(return_data("支付成功", data))
    else:
        return jsonify(return_data("订单未支付"))


@index_page.route("/getAdminInfo", methods=["POST"])
def getAdminInfo():
    '''
    获取客户的信息
    '''
    params = request.json
    result = Admin.query.filter_by(domain=params.get("domain")).first()
    res_data = result.to_json()
    print(res_data)
    data = {
        "admin_title": res_data.get("admin_title"),
        "admin_introduction": res_data.get("admin_introduction"),
        "group_introduction": res_data.get("group_introduction"),
        "now_price": res_data.get("now_price"),
        "old_price": res_data.get("old_price"),
        "pay_introduction": res_data.get("pay_introduction"),
        "subject_title":res_data.get("subject_title")
    }
    return jsonify(return_data("返回成功", data))


@index_page.route("/getQrcode", methods=["POST"])
def getQrcode():
    '''
    获取微信二维码和添加好友的备注信息
    '''
    params = request.json
    result = Admin.query.filter_by(domain=params.get("domain")).first()
    res_data = result.to_json()
    data = {
        "qrcode": res_data.get("wx_qrcode"),
        "mask": res_data.get("mask")
    }
    return jsonify(return_data("调用成功", data))
