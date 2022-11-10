import graphene
import greenhouse.schema


class Query(greenhouse.schema.Query, graphene.ObjectType):
    pass


schema = graphene.Schema(query=Query)
