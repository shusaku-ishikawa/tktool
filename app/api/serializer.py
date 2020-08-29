import os
from main.models import ScrapeRequest, Product
from rest_framework import serializers
import json

class JSONSerializerField(serializers.Field):
  def to_representation(self, value):
    return json.loads(value)

class ProductSerializer(serializers.ModelSerializer):
  
  class Meta:
    model = Product
    fields = [
      'asin',
      'jan',
      'Title',
      'Publisher',
      'PartNumber',
      'SalesRankings',
      'Binding',
      'ReleaseDate',
      'ListPriceValue',
      'ListPriceCurrency',
      'LandedPriceValue',
      'LandedPriceCurrency',
      'ShippingValue',
      'ShippingCurrency',
      'PointsValue',
      'PointsCurrency',
      'OfferListingCountNew',
      'LowestOfferListingNewPriceValue',
      'LowestOfferListingNewPriceCurrency',
      'LowestOfferListingNewShippingValue',
      'LowestOfferListingNewShippingCurrency',
      'LowestOfferListingNewPointsValue',
      'LowestOfferListingNewPointsCurrency',
      'OfferListingCountUsed',
      'LowestOfferListingUsedPriceValue',
      'LowestOfferListingUsedPriceCurrency',
      'LowestOfferListingUsedShippingValue',
      'LowestOfferListingUsedShippingCurrency',
      'LowestOfferListingUsedPointsValue',
      'LowestOfferListingUsedPointsCurrency',
      'WeightValue',
      'WeightUnit',
      'HeightValue',
      'HeightUnit',
      'LengthValue',
      'LengthUnit',
      'WidthValue',
      'WidthUnit',
    ]
  
class ScrapeRequestSerializer(serializers.ModelSerializer):
  products = ProductSerializer(many = True)

  class Meta:
    model = ScrapeRequest
    fields = ['products', 'requested_at', 'status_text', 'error']
