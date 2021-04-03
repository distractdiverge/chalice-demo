from aws_lambda_powertools.logging import Logger
from abc import ABC, abstractmethod


class AbstractParser(ABC):
    __BASE_CLASS = "DmBase"
    _logger: Logger

    def __init__(self, logger: Logger):
        self._logger = logger

    def _createJoinObject(self, **kwargs):
        """
        This function will create join models based on the criteria provided, and add the model to the sessoin

        :param kwargs:
          -joinObjectName: The string name of the object that joins Transaction to another object.
                          Example: PeriodAnalyticsDepositMaxTransaction
        -objectAName: The string name of the attribute on the joinObjectName that represents the
                          objectA party in the relationship. Example: PartnerAnalytic
        -objectA: The model object that is set to the joinObject's objectAName attribute
        -objectBName: The string name of the attribute on the joinObjectName that represents the
                          objectB party in the relationship. Example: PartnerAnalytic
        -objectB: The model object that is set to the joinObject's objectAName attribute
        -request_id: The string request_id to be used when creating any models

        """

        joinObjectName = kwargs.get("joinObjectName", None)
        objectAName = kwargs.get("objectAName", None)
        # check if name is in list to be converted to singular
        if objectAName in self.SINGULAR_OBJECT_NAMES:
            objectAName = objectAName[:-1]
        objectA = kwargs.get("objectA", None)

        objectBName = kwargs.get("objectBName", None)
        # check if objectBName in list to be converted to singular
        if objectBName in self.SINGULAR_OBJECT_NAMES:
            objectBName = objectBName[:-1]

        objectB = kwargs.get("objectB", None)
        requestId = kwargs.get("request_id", None)

        model = self._getmodel(joinObjectName, request_id=requestId)
        model.load(**{objectAName: objectA, objectBName: objectB})
        self._session.add(model)

    def _parse(self, data, **kwargs):
        childObjects = []
        childLists = []
        modelAttributes = {}
        for attr in data.keys():
            d = data[attr]
            if isinstance(d, dict) or isinstance(d, list):
                if isinstance(d, dict):
                    childObjects.append(attr)
                else:
                    # if it's a list and not in the Complex object list
                    if d not in models.OBJECTS_TO_FLATTEN:
                        childLists.append(attr)
            else:
                # simple attribute
                modelAttributes[attr] = d
        return {
            "attributes": modelAttributes,
            "objects": childObjects,
            "lists": childLists,
        }

    def _getmodel(self, key, **kwargs):
        if "parent" in kwargs and kwargs["parent"] is not None:
            key = "{}{}".format(key, kwargs["parent"])
        key = key.lower()

        try:
            if key not in self._MODEL_LOOKUP:
                if key.endswith("s"):
                    key = key[:-1]

            # print('[INFO] Model Classname: ' + self._MODEL_LOOKUP[key]['classname'])

            # Log the model
            if self._MODEL_LOOKUP[key]["table"] not in self.OBJECT_LOG:
                self.OBJECT_LOG[self._MODEL_LOOKUP[key]["table"]] = 0
            self.OBJECT_LOG[self._MODEL_LOOKUP[key]["table"]] += 1

            obj = getattr(models, self._MODEL_LOOKUP[key]["classname"])()
            if "request_id" in kwargs:
                obj.load(request_id=kwargs["request_id"])
            return obj
        except Exception as e:
            self._logger.error("[ERROR] Could not get model class from entity: " + key)
            self._logger.error(e)
            return False

    def _indexmodels(self, models):
        classDict = dict(
            [
                (name, cls)
                for name, cls in models.__dict__.items()
                if isinstance(cls, type) and cls.__module__ == "models"
            ]
        )

        # get table and model info for each model
        for classname in classDict:
            if classname == __BASE_CLASS:
                continue
            tmpObj = getattr(models, classname)
            self._TABLE_MODEL_LOOKUP[tmpObj.__tablename__] = classname.lower()
            cols = []
            attr = inspect.getmembers(tmpObj, lambda a: not (inspect.isroutine(a)))
            for a in attr:
                if not a[0].startswith("_"):
                    cols.append(a[0])
            self._MODEL_LOOKUP[classname.lower()] = {
                "table": tmpObj.__tablename__,
                "columns": cols,
                "classname": classname,
            }

    @abstractmethod
    def parse(input: str) -> object:
        pass
