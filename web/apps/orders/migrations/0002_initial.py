# Generated by Django 3.2 on 2021-04-21 01:57

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('users', '0001_initial'),
        ('orders', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='settings',
            name='elevators',
            field=models.ManyToManyField(blank=True, related_name='tenants', to='users.Elevator'),
        ),
        migrations.AddField(
            model_name='settings',
            name='menu',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='tenants', to='orders.menu'),
        ),
        migrations.AddField(
            model_name='settings',
            name='sameday_ordering_categories',
            field=models.ManyToManyField(blank=True, help_text='Same-Day Categories', related_name='_orders_settings_sameday_ordering_categories_+', to='orders.Category'),
        ),
        migrations.AddField(
            model_name='settings',
            name='tenant',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='users.tenant'),
        ),
        migrations.AddField(
            model_name='settings',
            name='tenant_floors',
            field=models.ManyToManyField(blank=True, related_name='floors', to='users.Floor'),
        ),
        migrations.AddField(
            model_name='settings',
            name='user_last_updated_approve_direct_signup',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='settings',
            name='user_last_updated_choice_location_deliver_to_reception',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='settings',
            name='user_last_updated_choice_location_restrict_locations',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='settings',
            name='user_last_updated_choice_payment_require_notation',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='settings',
            name='user_last_updated_choice_payment_restrict_to_house_account',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='settings',
            name='user_last_updated_user_email_validation',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='settings',
            name='user_last_updated_user_signup_method',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='settings',
            name='user_last_updated_value_location_deliver_to_reception',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='settings',
            name='user_last_updated_value_location_restrict_locations',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='paymentmethod',
            name='tenant',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='payment_methods', to='users.tenant'),
        ),
        migrations.AddField(
            model_name='paymentmethod',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='payment_methods', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='packageprice',
            name='menu',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='menu_prices', to='orders.menu'),
        ),
        migrations.AddField(
            model_name='packageprice',
            name='package',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='package_prices', to='orders.package'),
        ),
        migrations.AddField(
            model_name='packageprice',
            name='tenant',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='tenant_prices', to='users.tenant'),
        ),
        migrations.AddField(
            model_name='package',
            name='category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='packages', to='orders.category'),
        ),
        migrations.AddField(
            model_name='package',
            name='cost_type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='packages', to='orders.costtype'),
        ),
        migrations.AddField(
            model_name='package',
            name='courses_included',
            field=models.ManyToManyField(blank=True, related_name='mandatory_for_packages', to='orders.Course'),
        ),
        migrations.AddField(
            model_name='package',
            name='courses_select_from',
            field=models.ManyToManyField(blank=True, related_name='available_for_packages', to='orders.Course'),
        ),
        migrations.AddField(
            model_name='package',
            name='menu_items_included',
            field=models.ManyToManyField(blank=True, related_name='mandatory_for_packages', to='orders.MenuItem'),
        ),
        migrations.AddField(
            model_name='package',
            name='menu_items_select_from',
            field=models.ManyToManyField(blank=True, related_name='available_for_packages', to='orders.MenuItem'),
        ),
        migrations.AddField(
            model_name='package',
            name='packages_included',
            field=models.ManyToManyField(blank=True, related_name='mandatory_for_packages', to='orders.Package'),
        ),
        migrations.AddField(
            model_name='package',
            name='packages_select_from',
            field=models.ManyToManyField(blank=True, related_name='available_for_packages', to='orders.Package'),
        ),
        migrations.AddField(
            model_name='package',
            name='tags',
            field=models.ManyToManyField(blank=True, related_name='packages', to='orders.Tag'),
        ),
        migrations.AddField(
            model_name='orderstatus',
            name='changed_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='orderstatus',
            name='order',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='status', to='orders.orderbase'),
        ),
        migrations.AddField(
            model_name='orderpayment',
            name='order',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='payment', to='orders.orderbase'),
        ),
        migrations.AddField(
            model_name='orderpayment',
            name='payment',
            field=models.ForeignKey(help_text='Payment Reference', on_delete=django.db.models.deletion.CASCADE, related_name='orders', to='orders.paymentmethod'),
        ),
        migrations.AddField(
            model_name='orderpackage',
            name='logistics',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='packages', to='orders.orderlogistics'),
        ),
        migrations.AddField(
            model_name='orderpackage',
            name='order',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='packages', to='orders.orderbase'),
        ),
        migrations.AddField(
            model_name='orderpackage',
            name='package',
            field=models.ForeignKey(help_text='Package', on_delete=django.db.models.deletion.CASCADE, related_name='packages', to='orders.package'),
        ),
        migrations.AddField(
            model_name='ordernote',
            name='logistics',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='note', to='orders.orderlogistics'),
        ),
        migrations.AddField(
            model_name='ordernote',
            name='order',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='notes', to='orders.orderbase'),
        ),
        migrations.AddField(
            model_name='ordermenuitem',
            name='course',
            field=models.ForeignKey(blank=True, help_text='Course', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='items', to='orders.ordercourse'),
        ),
        migrations.AddField(
            model_name='ordermenuitem',
            name='menu_item',
            field=models.ForeignKey(help_text='Menu Item', on_delete=django.db.models.deletion.CASCADE, related_name='orders', to='orders.menuitem'),
        ),
        migrations.AddField(
            model_name='ordermenuitem',
            name='order',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='orders.orderbase'),
        ),
        migrations.AddField(
            model_name='ordermenuitem',
            name='package',
            field=models.ForeignKey(help_text='Package', on_delete=django.db.models.deletion.CASCADE, related_name='items', to='orders.orderpackage'),
        ),
        migrations.AddField(
            model_name='orderlogistics',
            name='addons',
            field=models.ManyToManyField(blank=True, help_text='AddOns', related_name='logistics', to='orders.AddOn'),
        ),
        migrations.AddField(
            model_name='orderlogistics',
            name='building',
            field=models.ForeignKey(blank=True, help_text='Building', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='users.building'),
        ),
        migrations.AddField(
            model_name='orderlogistics',
            name='calendars',
            field=models.ManyToManyField(blank=True, related_name='logistics', to='orders.Calendar'),
        ),
        migrations.AddField(
            model_name='orderlogistics',
            name='location',
            field=models.ForeignKey(blank=True, help_text='Location', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='logistics', to='orders.location'),
        ),
        migrations.AddField(
            model_name='orderlogistics',
            name='order',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='logistics', to='orders.orderbase'),
        ),
        migrations.AddField(
            model_name='orderhistory',
            name='changed_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='orderhistory',
            name='order',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='history', to='orders.orderbase'),
        ),
        migrations.AddField(
            model_name='orderdeliverywindow',
            name='building',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='deliveries', to='users.building'),
        ),
        migrations.AddField(
            model_name='ordercoursemodification',
            name='course',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ordered_modifications', to='orders.ordercourse'),
        ),
        migrations.AddField(
            model_name='ordercoursemodification',
            name='menu_item',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='modifications', to='orders.ordermenuitem'),
        ),
        migrations.AddField(
            model_name='ordercoursemodification',
            name='modification',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='ordered_mods', to='orders.coursemodificationoption'),
        ),
        migrations.AddField(
            model_name='ordercourse',
            name='course',
            field=models.ForeignKey(help_text='Course', on_delete=django.db.models.deletion.CASCADE, related_name='orders', to='orders.course'),
        ),
        migrations.AddField(
            model_name='ordercourse',
            name='order',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='courses', to='orders.orderbase'),
        ),
        migrations.AddField(
            model_name='ordercourse',
            name='package',
            field=models.ForeignKey(help_text='Package', on_delete=django.db.models.deletion.CASCADE, related_name='courses', to='orders.orderpackage'),
        ),
        migrations.AddField(
            model_name='orderbase',
            name='customer',
            field=models.ForeignKey(blank=True, help_text='Customer', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='orders', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='orderbase',
            name='repeat',
            field=models.ForeignKey(blank=True, help_text='Order Repeat', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='orders', to='orders.orderrepeat'),
        ),
        migrations.AddField(
            model_name='orderaddon',
            name='addon',
            field=models.ForeignKey(blank=True, help_text='AddOn', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='addons_staff', to='orders.addon'),
        ),
        migrations.AddField(
            model_name='orderaddon',
            name='cost_type',
            field=models.ForeignKey(blank=True, help_text='Cost Type', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='addons_staff', to='orders.costtype'),
        ),
        migrations.AddField(
            model_name='orderaddon',
            name='logistics',
            field=models.ForeignKey(blank=True, help_text='Setup/Delivery', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='addons_staff', to='orders.orderlogistics'),
        ),
        migrations.AddField(
            model_name='orderaddon',
            name='order',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='addons_staff', to='orders.orderbase'),
        ),
        migrations.AddField(
            model_name='orderaddon',
            name='package',
            field=models.ForeignKey(blank=True, help_text='Package', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='addons_staff', to='orders.orderpackage'),
        ),
        migrations.AddField(
            model_name='menuitem',
            name='tags',
            field=models.ManyToManyField(blank=True, related_name='menu_items', to='orders.Tag'),
        ),
        migrations.AddField(
            model_name='menu',
            name='packages',
            field=models.ManyToManyField(blank=True, related_name='menus_containing', to='orders.Package'),
        ),
        migrations.AddField(
            model_name='location',
            name='building',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='locations', to='users.building'),
        ),
        migrations.AddField(
            model_name='location',
            name='tenant',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='locations', to='users.tenant'),
        ),
        migrations.AddField(
            model_name='coursemodificationoption',
            name='course',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='modifications', to='orders.course'),
        ),
        migrations.AddField(
            model_name='coursemodificationoption',
            name='menu',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='modifications', to='orders.menu'),
        ),
        migrations.AddField(
            model_name='course',
            name='menu_items_included',
            field=models.ManyToManyField(blank=True, related_name='mandatory_for_courses', to='orders.MenuItem'),
        ),
        migrations.AddField(
            model_name='course',
            name='menu_items_select_from',
            field=models.ManyToManyField(blank=True, related_name='available_for_courses', to='orders.MenuItem'),
        ),
        migrations.AddField(
            model_name='course',
            name='tags',
            field=models.ManyToManyField(blank=True, related_name='courses', to='orders.Tag'),
        ),
        migrations.AddField(
            model_name='billingrecord',
            name='changed_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='billingrecord',
            name='order',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='billing_record', to='orders.orderbase'),
        ),
        migrations.AddField(
            model_name='addonprice',
            name='addon',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='prices', to='orders.addon'),
        ),
        migrations.AddField(
            model_name='addonprice',
            name='menu',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='addons', to='orders.menu'),
        ),
        migrations.AddField(
            model_name='addonprice',
            name='tenant',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='addon_prices', to='users.tenant'),
        ),
        migrations.AddField(
            model_name='addon',
            name='cost_type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='addons', to='orders.costtype'),
        ),
        migrations.AlterUniqueTogether(
            name='addonprice',
            unique_together={('addon', 'menu')},
        ),
    ]
