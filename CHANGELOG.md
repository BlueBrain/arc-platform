1.0.13 (unreleased)
-------------------

- Nothing changed yet.


1.0.12 (2020-08-04)
-------------------

- Added:
  *  user profile with an option to unsubscribe from email reminders to archive supplies.


1.0.11 (2020-06-25)
-------------------

- Added:
  * user workflow documentaion
- Changed:
  * unification of category item labels


1.0.10 (2020-06-23)
-------------------

- Added:
  * SOP to manage users, their roles and passwords
  * completed match supplier notification
  * responsive design for:
    * page titles and action buttons (Dashboard view, list of supplies and requests, users)
    * the menu
    * filter inputs for list views (supplies, requests, users)
- Changed:
  * validated match email notification according to QA feedback
  * make attributed requests in supply details page visible only for moderators and validators
  * seed scripts: rename @apptitude.ch accounts to prevent sending automated emails to that domain
- Fixed:
  * update_by field value for User model
  * permissions for attribution validation actions (set to be available to validator role only)
  * supply available qty calculation: take into consideration completed matches
  * request expiring validator notification template name


1.0.9 (2020-06-11)
------------------

- Added:
  * requester user role
  * request submission, rejection and validation
  * match completed status
  * ability to change request priority by privileged users
  * email notification about request submission/rejection/validation
  * prefill request and supply from with user data (not only Switch related)
  * "to close" filter in requests view
  * email reminder for suppliers to close unavailable supply
  * Sentry error tracking
  * page reload when users uses browser's back button
  * documentation for configuration environment variables
- Changed:
  * validated match email template (according to feedback from Lab Spiez)
  * supply archive reminder email template (according to QA)
- Fixed:
  * supply page pagination location
  * password change for privileged users
  * various permission issues


1.0.8 (2020-05-11)
------------------

- Added:
  * feature to request creation of vocabulary items
  * capability to open archived requests
  * confederation logo and technical support mail address in home page
  * link to SOP for moderators and validators in the footer


1.0.7 (2020-05-08)
------------------

- Added:
  * natural request ordering
  * SMTP backend with HTTP_PROXY support
  * an email notification to validators when a new match created
  * request expiration
  * rejected and on hold status for attribution
  * visually distinguishable uat env
  * case insensitive login
  * import of supplies and requests
  * change password page for non-switch users
  * prefilling for supply form with switch user data
  * labels in request and supply detail
- Updated dashboard wording
- Fixed:
  * select inputs not working in IE/Edge
  * attribution form picking values from the first match in a list


1.0.6 (2020-04-28)
------------------

- Added category filter in request ans supply lists
- Changed supply status wording
- Show 100 items per page in request and supply lists


1.0.5 (2020-04-24)
------------------

- Fixed bug in supply & request creation form causing selects to
be enabled without parent select being filled and displaying
wrong items


1.0.4 (2020-04-23)
------------------

- Improved supply export


1.0.3 (2020-04-23)
------------------

- Updated wording for consistency in supply form


1.0.2 (2020-04-23)
------------------

- Added optional filed for catalog number of a supply
- Split supply pickup address in multiple fields
- Added a help text in supply creation form
- Manufacturer and name are now mandatory for requests and supplies
- Reworked the "My product is not in the list" feature to automatically
create new manufacturers and items after moderator or validator approval


1.0.1 (2020-04-21)
------------------

- Added production seed script from Jean-Denis Courcol
- Modified homepage texts
- Added help email addresses in footer


1.0.0 (2020-04-20)
------------------

- Style and layout updates


0.1.2 (2020-04-17)
------------------

- New homepage
- Impressum
- Terms of Service
- Help
- Password login


0.1.1 (2020-04-16)
------------------

- First batch of changes after moderator feedback.


0.1.0 (2020-04-09)
------------------
