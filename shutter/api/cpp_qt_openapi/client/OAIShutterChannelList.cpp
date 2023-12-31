/**
 * FastAPI
 * No description provided (generated by Openapi Generator https://github.com/openapitools/openapi-generator)
 *
 * The version of the OpenAPI document: 0.1.0
 *
 * NOTE: This class is auto generated by OpenAPI Generator (https://openapi-generator.tech).
 * https://openapi-generator.tech
 * Do not edit the class manually.
 */

#include "OAIShutterChannelList.h"

#include <QDebug>
#include <QJsonArray>
#include <QJsonDocument>
#include <QObject>

#include "OAIHelpers.h"

namespace OpenAPI {

OAIShutterChannelList::OAIShutterChannelList(QString json) {
    this->initializeModel();
    this->fromJson(json);
}

OAIShutterChannelList::OAIShutterChannelList() {
    this->initializeModel();
}

OAIShutterChannelList::~OAIShutterChannelList() {}

void OAIShutterChannelList::initializeModel() {

    m_shutter_list_isSet = false;
    m_shutter_list_isValid = false;
}

void OAIShutterChannelList::fromJson(QString jsonString) {
    QByteArray array(jsonString.toStdString().c_str());
    QJsonDocument doc = QJsonDocument::fromJson(array);
    QJsonObject jsonObject = doc.object();
    this->fromJsonObject(jsonObject);
}

void OAIShutterChannelList::fromJsonObject(QJsonObject json) {

    m_shutter_list_isValid = ::OpenAPI::fromJsonValue(m_shutter_list, json[QString("shutter_list")]);
    m_shutter_list_isSet = !json[QString("shutter_list")].isNull() && m_shutter_list_isValid;
}

QString OAIShutterChannelList::asJson() const {
    QJsonObject obj = this->asJsonObject();
    QJsonDocument doc(obj);
    QByteArray bytes = doc.toJson();
    return QString(bytes);
}

QJsonObject OAIShutterChannelList::asJsonObject() const {
    QJsonObject obj;
    if (m_shutter_list.size() > 0) {
        obj.insert(QString("shutter_list"), ::OpenAPI::toJsonValue(m_shutter_list));
    }
    return obj;
}

QList<QString> OAIShutterChannelList::getShutterList() const {
    return m_shutter_list;
}
void OAIShutterChannelList::setShutterList(const QList<QString> &shutter_list) {
    m_shutter_list = shutter_list;
    m_shutter_list_isSet = true;
}

bool OAIShutterChannelList::is_shutter_list_Set() const{
    return m_shutter_list_isSet;
}

bool OAIShutterChannelList::is_shutter_list_Valid() const{
    return m_shutter_list_isValid;
}

bool OAIShutterChannelList::isSet() const {
    bool isObjectUpdated = false;
    do {
        if (m_shutter_list.size() > 0) {
            isObjectUpdated = true;
            break;
        }
    } while (false);
    return isObjectUpdated;
}

bool OAIShutterChannelList::isValid() const {
    // only required properties are required for the object to be considered valid
    return m_shutter_list_isValid && true;
}

} // namespace OpenAPI
