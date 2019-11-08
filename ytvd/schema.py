import graphene
import subscriptions.schema as subs


class Query(subs.Query, graphene.ObjectType):
    pass

schema = graphene.Schema(query=Query)
