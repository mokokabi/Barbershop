from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.forms import AdminPasswordChangeForm
from mainapp.models import Barbery, Reservation, TimeSlot, UserProfile
from mainapp.forms import BarberyCreationForm, ReservationForm, AddSlotsAdminForm
from mainapp.list_filters import SpecialTimesFilter
# Register your models here.


@admin.register(Barbery)
class BarberyAdmin(admin.ModelAdmin):
    add_form = BarberyCreationForm
    # fields = ('name', ('first_name', 'last_name'), 'email', 'address', 'is_active', )
    fieldsets = (
        (_('Barbery info'), {'fields': (('name', 'is_active'), 'address', )}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('name', 'address', 'first_name', 'last_name', 'password1', 'password2'),
        }),
    )
    change_password_form = AdminPasswordChangeForm
    list_display = ('name', 'first_name', 'last_name', 'address', 'num_of_time_slots', 'num_of_reservations', 'is_active', )
    search_fields = ('name', 'first_name', 'last_name', 'address', )
    list_filter = ('is_active', )
    ordering = ('name', )

    def get_fieldsets(self, request, obj=None):
        if not obj:
            return self.add_fieldsets
        return super(BarberyAdmin, self).get_fieldsets(request, obj)

    def get_form(self, request, obj=None, **kwargs):
        """
        Use special form during user creation
        """
        defaults = {}
        if obj is None:
            defaults['form'] = self.add_form
        defaults.update(kwargs)
        return super(BarberyAdmin, self).get_form(request, obj, **defaults)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    fields = ('email', ('first_name', 'last_name'), 'is_active', )
    list_display = ('email', 'first_name', 'last_name', 'is_active', )
    search_fields = ('email', 'first_name', 'last_name', )
    list_filter = ('is_active', )
    ordering = ('email',)


@admin.register(TimeSlot)
class TimeSlotAdmin(admin.ModelAdmin):
    add_form = AddSlotsAdminForm
    add_fieldsets = (
        (None, {
            'classes': ('wide', ),
            'fields': ('barbery', 'start_time', 'duration', 'add_for_a_week', ),
        }),
    )
    readonly_fields = ('reserved', 'created_date', )
    exclude = ('created_date', )
    fields = ('barbery', ('start_time', 'duration'), 'created_date', 'reserved', )
    list_display = ('__str__', 'barbery', 'start_time', 'duration', 'reserved',)
    search_fields = ('barbery__name', 'barbery__first_name', 'barbery__last_name', 'barbery__address',)
    list_filter = (SpecialTimesFilter, 'reserved', )
    ordering = ('-start_time', )
    raw_id_fields = ('barbery', )

    def save_model(self, request, obj, form, change):
        form.save()

    def get_fieldsets(self, request, obj=None):
        if not obj:
            return self.add_fieldsets
        return super(TimeSlotAdmin, self).get_fieldsets(request, obj)

    def get_form(self, request, obj=None, **kwargs):
        """
        Use special form during user creation
        """
        defaults = {}
        if obj is None:
            defaults['form'] = self.add_form
        defaults.update(kwargs)
        return super(TimeSlotAdmin, self).get_form(request, obj, **defaults)


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    readonly_fields = ('created_date', )
    exclude = ()
    fields = ('user', 'slot', 'created_date', )
    list_display = ('__str__', 'user', 'slot')
    # list_display = ('__str__', 'user', 'barbery', 'slot__start_time', 'slot__duration', )
    search_fields = ('user__first_name', 'user__last_name', 'user__email', 'slot__barbery__name',
                     'slot__barbery__address')
    ordering = ('-created_date', )
    raw_id_fields = ('slot', 'user', )
