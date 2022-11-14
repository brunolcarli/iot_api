import graphene
import greenhouse.schema


class Query(greenhouse.schema.Query, graphene.ObjectType):
    pass

class Mutation(greenhouse.schema.Mutation, graphene.ObjectType):
    pass


schema = graphene.Schema(query=Query, mutation=Mutation)
