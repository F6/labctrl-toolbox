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

/*
 * OAIValidationError_loc_inner.h
 *
 * 
 */

#ifndef OAIValidationError_loc_inner_H
#define OAIValidationError_loc_inner_H

#include <QJsonObject>


#include "OAIEnum.h"
#include "OAIObject.h"

namespace OpenAPI {

class OAIValidationError_loc_inner : public OAIObject {
public:
    OAIValidationError_loc_inner();
    OAIValidationError_loc_inner(QString json);
    ~OAIValidationError_loc_inner() override;

    QString asJson() const override;
    QJsonObject asJsonObject() const override;
    void fromJsonObject(QJsonObject json) override;
    void fromJson(QString jsonString) override;

    virtual bool isSet() const override;
    virtual bool isValid() const override;

private:
    void initializeModel();
};

} // namespace OpenAPI

Q_DECLARE_METATYPE(OpenAPI::OAIValidationError_loc_inner)

#endif // OAIValidationError_loc_inner_H
