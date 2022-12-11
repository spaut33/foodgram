from api.serializers.subscribe_serializers import SubscriptionSerializer



def get_subscription_serializer(*args, **kwargs):
    return SubscriptionSerializer(
        kwargs.get('queryset'),
        context={'request': kwargs.get('request')},
        many=True,
    ).data
