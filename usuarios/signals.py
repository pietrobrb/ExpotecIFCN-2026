from allauth.socialaccount.signals import social_account_updated, social_account_added
from django.dispatch import receiver

@receiver(social_account_updated)
@receiver(social_account_added)
def update_user_data_from_social_account(request, sociallogin, **kwargs):
    user = sociallogin.user
    extra_data = sociallogin.account.extra_data
    provider = sociallogin.account.get_provider()

    mapped_data = provider.extract_common_fields(extra_data)

    # Update user fields based on mapped data
    for field, value in mapped_data.items():
        setattr(user, field, value)

    # Save updated user data
    user.save()
