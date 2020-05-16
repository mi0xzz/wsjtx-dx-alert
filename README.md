# What is wsjtx-dx-alert

_wsjtx-dx-alert_ is a custom Python module that I have developed to assist with providing notifications upon successful decodes from the WSJTX software.

The intention was to be able to leave WSJTX running on my PC while monitoring the 2m or 6m band and then have a message sent to my phone if something interesting has been seen
which could include DX or just a new call sign that I've not managed a QSO with.

The _wsjtx-dx-module_ is intended to run as part of a larger setup which is summarised as follows:

WSJTX -> wsjtx-dx-alert -> MQTT -> Node-RED -> Telegram Bot

First of all, the WSJTX software should be configured to send

