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

#include "OAIShutterChannelOperation.h"

#include <QDebug>
#include <QJsonArray>
#include <QJsonDocument>
#include <QObject>

#include "OAIHelpers.h"

namespace OpenAPI {

OAIShutterChannelOperation::OAIShutterChannelOperation(QString json) {
    this->initializeModel();
    this->fromJson(json);
}

OAIShutterChannelOperation::OAIShutterChannelOperation() {
    this->initializeModel();
}

OAIShutterChannelOperation::~OAIShutterChannelOperation() {}

void OAIShutterChannelOperation::initializeModel() {

    m_action_isSet = false;
    m_action_isValid = false;
}

void OAIShutterChannelOperation::fromJson(QString jsonString) {
    QByteArray array(jsonString.toStdString().c_str());
    QJsonDocument doc = QJsonDocument::fromJson(array);
    QJsonObject jsonObject = doc.object();
    this->fromJsonObject(jsonObject);
}

void OAIShutterChannelOperation::fromJsonObject(QJsonObject json) {

    m_action_isValid = ::OpenAPI::fromJsonValue(m_action, json[QString("action")]);
    m_action_isSet = !json[QString("action")].isNull() && m_action_isValid;
}

QString OAIShutterChannelOperation::asJson() const {
    QJsonObject obj = this->asJsonObject();
    QJsonDocument doc(obj);
    QByteArray bytes = doc.toJson();
    return QString(bytes);
}

QJsonObject OAIShutterChannelOperation::asJsonObject() const {
    QJsonObject obj;
    if (m_action.isSet()) {
        obj.insert(QString("action"), ::OpenAPI::toJsonValue(m_action));
    }
    return obj;
}

OAIShutterAction OAIShutterChannelOperation::getAction() const {
    return m_action;
}
void OAIShutterChannelOperation::setAction(const OAIShutterAction &action) {
    m_action = action;
    m_action_isSet = true;
}

bool OAIShutterChannelOperation::is_action_Set() const{
    return m_action_isSet;
}

bool OAIShutterChannelOperation::is_action_Valid() const{
    return m_action_isValid;
}

bool OAIShutterChannelOperation::isSet() const {
    bool isObjectUpdated = false;
    do {
        if (m_action.isSet()) {
            isObjectUpdated = true;
            break;
        }
    } while (false);
    return isObjectUpdated;
}

bool OAIShutterChannelOperation::isValid() const {
    // only required properties are required for the object to be considered valid
    return m_action_isValid && true;
}

} // namespace OpenAPI
