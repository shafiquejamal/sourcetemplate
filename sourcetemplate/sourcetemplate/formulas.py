from django.conf import settings

def mask_toggle(number_to_mask_or_unmask):
	return int(number_to_mask_or_unmask) ^ settings.MASKING_KEY