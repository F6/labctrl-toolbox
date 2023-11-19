QT += network

HEADERS += \
# Models
    $${PWD}/OAIHTTPValidationError.h \
    $${PWD}/OAIServerStatusReport.h \
    $${PWD}/OAIShutterAction.h \
    $${PWD}/OAIShutterChannelList.h \
    $${PWD}/OAIShutterChannelOperation.h \
    $${PWD}/OAIShutterState.h \
    $${PWD}/OAIShutterStateReport.h \
    $${PWD}/OAIToken.h \
    $${PWD}/OAIValidationError.h \
    $${PWD}/OAIValidationError_loc_inner.h \
# APIs
    $${PWD}/OAIDefaultApi.h \
# Others
    $${PWD}/OAIHelpers.h \
    $${PWD}/OAIHttpRequest.h \
    $${PWD}/OAIObject.h \
    $${PWD}/OAIEnum.h \
    $${PWD}/OAIHttpFileElement.h \
    $${PWD}/OAIServerConfiguration.h \
    $${PWD}/OAIServerVariable.h \
    $${PWD}/OAIOauth.h

SOURCES += \
# Models
    $${PWD}/OAIHTTPValidationError.cpp \
    $${PWD}/OAIServerStatusReport.cpp \
    $${PWD}/OAIShutterAction.cpp \
    $${PWD}/OAIShutterChannelList.cpp \
    $${PWD}/OAIShutterChannelOperation.cpp \
    $${PWD}/OAIShutterState.cpp \
    $${PWD}/OAIShutterStateReport.cpp \
    $${PWD}/OAIToken.cpp \
    $${PWD}/OAIValidationError.cpp \
    $${PWD}/OAIValidationError_loc_inner.cpp \
# APIs
    $${PWD}/OAIDefaultApi.cpp \
# Others
    $${PWD}/OAIHelpers.cpp \
    $${PWD}/OAIHttpRequest.cpp \
    $${PWD}/OAIHttpFileElement.cpp \
    $${PWD}/OAIOauth.cpp
