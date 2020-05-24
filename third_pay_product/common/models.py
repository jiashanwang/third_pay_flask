# coding: utf-8
from sqlalchemy import Column, DateTime, Float, Integer, String
from flask_sqlalchemy import SQLAlchemy
from application import db


# db = SQLAlchemy()


class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    domain = db.Column(db.String(255), nullable=False, unique=True, info='域名：一个客户一个域名，SaaS，用于区分不同的客户，（每个客户下面都有自己的粉丝群）')
    phone = db.Column(db.String(255), info='用户手机号')
    merchant_order_number = db.Column(db.String(255), info='商户订单号')
    create_time = db.Column(db.DateTime, info='订单创建时间')
    pay_time = db.Column(db.DateTime, info='订单支付时间')
    pay_type = db.Column(db.String(255), info='支付宝：alipay\\n微信：wechat')
    qr_price = db.Column(db.Float(8), info='返回的二维码金额（元）')
    pay_price = db.Column(db.Float(8), info='用户最终需要支付的金额（元）')
    cloud_order_number = db.Column(db.String(255), info='云端订单号')
    qr_type = db.Column(db.String(255), info='fixed：个人版固额二维码\\nbusiness：商业版收款码\\nno_fixed：个人版非固额二维码\\noriginal：原价')

    def __init__(self, domain,phone,merchant_order_number,create_time, id=None):
        self.domain = domain
        self.phone = phone
        self.merchant_order_number = merchant_order_number
        self.create_time = create_time
        if id is not None:
            self.id = id

