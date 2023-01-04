from rest_framework import serializers
from .models import Item, ItemCategory, ItemSubCategory
from utils.functions import current_user
from django.utils import timezone


class ItemSerializer(serializers.ModelSerializer):
    item_category_name = serializers.ReadOnlyField(source="item_category.name", allow_null=True)
    item_type_display = serializers.ReadOnlyField(source="get_item_type_display", allow_null=True)

    class Meta:
        model = Item
        fields = "__all__"
        read_only_fields = ['created_by', 'created_date_ad', 'created_date_bs']

    def to_representation(self, instance):
        my_fields = {'item_category', 'image',
                     'item_category_name'}
        data = super().to_representation(instance)
        for field in my_fields:
            try:
                if not data[field]:
                    data[field] = ""
            except KeyError:
                pass
        return data

    def create(self, validated_data):
        if validated_data['code'] == "":
            item_count = Item.objects.count()
            max_id = str(item_count + 1)
            unique_id = "ITM-" + max_id.zfill(6)
            validated_data['code'] = unique_id
        date_now = timezone.now()
        print(f"Image data ***** {type(validated_data['image'])}")
        print(validated_data)
        validated_data['created_by'] = current_user.get_created_by(self.context)
        item = Item.objects.create(**validated_data, created_date_ad=date_now)
        return item


class ItemCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemCategory
        fields = "__all__"
        read_only_fields = ['created_by', 'created_date_ad', 'created_date_bs']

    def create(self, validated_data):
        # empty field for display order
        if validated_data['display_order'] == '':
            validated_data['display_order'] = None
        if validated_data['code'] == "" or validated_data['code'] is None:
            item_count = ItemCategory.objects.count()
            max_id = str(item_count + 1)
            unique_id = "ITC-" + max_id.zfill(6)
            validated_data['code'] = unique_id
        date_now = timezone.now()
        validated_data['created_by'] = current_user.get_created_by(self.context)
        item_category = ItemCategory.objects.create(**validated_data, created_date_ad=date_now)
        return item_category


class ItemSubCategorySerializer(serializers.ModelSerializer):
    item_category_name = serializers.ReadOnlyField(source='item_category.name', allow_null=True)

    class Meta:
        model = ItemSubCategory
        fields = "__all__"
        read_only_fields = ['created_by', 'created_date_ad', 'created_date_bs']

    def create(self, validated_data):
        # empty field for display order
        if validated_data['display_order'] == '':
            validated_data['display_order'] = None
        if validated_data['code'] == "" or validated_data['code'] is None:
            item_count = ItemSubCategory.objects.count()
            max_id = str(item_count + 1)
            unique_id = "ISC-" + max_id.zfill(6)
            validated_data['code'] = unique_id

        date_now = timezone.now()
        validated_data['created_by'] = current_user.get_created_by(self.context)
        item_sub_category = ItemSubCategory.objects.create(**validated_data, created_date_ad=date_now)
        return item_sub_category
