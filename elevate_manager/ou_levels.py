# Modul containing functions for handling the actual business logic
# of the application
# TODO: add argument which should be the same as the response type
#       from mo.get_org_unit_levels
# TODO: add return type
def get_new_org_unit_for_engagement():
    """
    Extract the OU level of the OU where the manager update
    occurred and OU levels of the OUs of all the units where
    the manager has engagements and compare the OU level.

    NOTE: log an error if the manager has more than one engagement!

    If the OU level of the OU where the manager update
    occurred is higher than ALL the OU levels of the OUs
    of all the units where the manager has engagements then
    return the proper (Quicktype) object of the OU where the
    manager update occurred and else return None.
    """
    pass
