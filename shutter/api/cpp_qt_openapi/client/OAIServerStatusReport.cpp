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

#include "OAIServerStatusReport.h"

#include <QDebug>
#include <QJsonArray>
#include <QJsonDocument>
#include <QObject>

#include "OAIHelpers.h"

namespace OpenAPI {

OAIServerStatusReport::OAIServerStatusReport(QString json) {
    this->initializeModel();
    this->fromJson(json);
}

OAIServerStatusReport::OAIServerStatusReport() {
    this->initializeModel();
}

OAIServerStatusReport::~OAIServerStatusReport() {}

void OAIServerStatusReport::initializeModel() {

    m_status_isSet = false;
    m_status_isValid = false;
}

void OAIServerStatusReport::fromJson(QString jsonString) {
    QByteArray array(jsonString.toStdString().c_str());
    QJsonDocument doc = QJsonDocument::fromJson(array);
    QJsonObject jsonObject = doc.object();
    this->fromJsonObject(jsonObject);
}

void OAIServerStatusReport::fromJsonObject(QJsonObject json) {

    m_status_isValid = ::OpenAPI::fromJsonValue(m_status, json[QString("status")]);
    m_status_isSet = !json[QString("status")].isNull() && m_status_isValid;
}

QString OAIServerStatusReport::asJson() const {
    QJsonObject obj = this->asJsonObject();
    QJsonDocument doc(obj);
    QByteArray bytes = doc.toJson();
    return QString(bytes);
}

QJsonObject OAIServerStatusReport::asJsonObject() const {
    QJsonObject obj;
    if (m_status_isSet) {
        obj.insert(QString("status"), ::OpenAPI::toJsonValue(m_status));
    }
    return obj;
}

QString OAIServerStatusReport::getStatus() const {
    return m_status;
}
void OAIServerStatusReport::setStatus(const QString &status) {
    m_status = status;
    m_status_isSet = true;
}

bool OAIServerStatusReport::is_status_Set() const{
    return m_status_isSet;
}

bool OAIServerStatusReport::is_status_Valid() const{
    return m_status_isValid;
}

bool OAIServerStatusReport::isSet() const {
    bool isObjectUpdated = false;
    do {
        if (m_status_isSet) {
            isObjectUpdated = true;
            break;
        }
    } while (false);
    return isObjectUpdated;
}

bool OAIServerStatusReport::isValid() const {
    // only required properties are required for the object to be considered valid
    return m_status_isValid && true;
}

} // namespace OpenAPI
