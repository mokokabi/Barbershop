from datetime import datetime

from rest_framework import generics, serializers, filters
from rest_framework.permissions import IsAuthenticated
from mainapp.models import Barbery, UserProfile, TimeSlot, Reservation
from mainapp.serializers import (BarberyListSerializer, BarberyTimeSlotListSerializer,
                                 UserProfileSerializer, UserSignUpSerializer, ReservationSerializer,
                                 UserPasswordSerializer, UserReserveTimeSlotSerializer, TimeSlotListSerializer)
from mainapp.permissions import IsOwnerOfReservation


class BarberyListView(generics.ListAPIView):
    queryset = Barbery.objects.all()
    serializer_class = BarberyListSerializer
    permission_classes = []


class BarberyProfileView(generics.RetrieveAPIView):
    queryset = Barbery.objects.all()
    serializer_class = BarberyListSerializer
    permission_classes = []


# TODO is this true or not?!
# class BarberyTimeSlotsListView(generics.RetrieveAPIView):
#     queryset = Barbery.objects.all()
#     serializer_class = BarberyTimeSlotListSerializer
#     permission_classes = []


class BarberyTimeSlotsListView(generics.ListAPIView):
    serializer_class = TimeSlotListSerializer
    permission_classes = []

    def get_queryset(self):
        pk = self.kwargs.get('pk')
        return TimeSlot.objects.filter(barbery__pk=pk)


class UserSignUpView(generics.CreateAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = UserSignUpSerializer
    permission_classes = []


class UserActionsView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = (IsAuthenticated, )

    def get_object(self):
        user = self.request.user
        user_profile = UserProfile.objects.get(pk=user.pk)
        return user_profile


class UserReservationsView(generics.ListAPIView):
    serializer_class = ReservationSerializer
    permission_classes = (IsAuthenticated, )

    def get_queryset(self):
        user = self.request.user
        user_profile = UserProfile.objects.get(pk=user.pk)
        passed = self.request.query_params.get('passed', None)
        if passed is None:
            return user_profile.reservations.all()
        elif passed == '0':
            return user_profile.reservations.filter(slot__start_time__gt=datetime.now())
        elif passed == '1':
            return user_profile.reservations.filter(slot__start_time__lte=datetime.now())


class UserChangePasswordView(generics.UpdateAPIView):
    serializer_class = UserPasswordSerializer
    permission_classes = (IsAuthenticated, )

    def get_object(self):
        user = self.request.user
        user_profile = UserProfile.objects.get(pk=user.pk)
        return user_profile


class UserReserveTimeSlotView(generics.UpdateAPIView):
    queryset = TimeSlot.objects.all()
    serializer_class = UserReserveTimeSlotSerializer
    permission_classes = (IsAuthenticated, )

    def perform_update(self, serializer):
        serializer.validated_data['user'] = self.request.user
        return serializer.update(serializer.instance, serializer.validated_data)


class UserCancelReservationView(generics.DestroyAPIView):
    queryset = Reservation.objects.all()
    permission_classes = (IsAuthenticated, IsOwnerOfReservation, )

    def perform_destroy(self, instance):
        if not instance.can_cancel():
            raise serializers.ValidationError("time has passed and can't be cancelled.")
        instance.cancel()
        return super().perform_destroy(instance)


class UserViewTimeSlots(generics.ListAPIView):
    queryset = TimeSlot.get_not_passed()
    serializer_class = TimeSlotListSerializer
    filter_backends = (filters.SearchFilter, )
    search_fields = ('barbery__username', 'barbery__email', 'barbery__first_name', 'barbery__last_name', )

    # def get_queryset(self):
        # search_dict = self.request.query_params
        # return TimeSlot.perform_search(search_dict)
        # return
