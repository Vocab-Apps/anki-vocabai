import os
import sys
import logging
import traceback

addon_dir = os.path.dirname(os.path.realpath(__file__))
external_dir = os.path.join(addon_dir, 'external')
sys.path.insert(0, external_dir)


if hasattr(sys, '_pytest_mode'):
    # don't do anything
    pass 
else:
    from . import addon

    # initalize logger, basic logging with debug logging level
    ENABLE_CONSOLE_LOGGING = False
    if ENABLE_CONSOLE_LOGGING:
        logging.basicConfig(
            format='%(asctime)s %(levelname)s %(filename)s:%(lineno)d %(message)s',
            level=logging.DEBUG,
            handlers=[logging.StreamHandler(sys.stdout)])

    ENABLE_SENTRY_CRASH_REPORTING = True
    if ENABLE_SENTRY_CRASH_REPORTING:
        def sentry_filter(event, hint):
            if 'exc_info' in hint:
                exc_type, exc_value, tb = hint['exc_info']

                # do we recognize the paths in this stack trace ?
                relevant_exception = False
                stack_summary = traceback.extract_tb(tb)
                for stack_frame in stack_summary:
                    filename = stack_frame.filename
                    # TODO change addon id
                    if 'anki-vocabai' in filename or '111623432' in filename:
                        relevant_exception = True
                
                # if not, discard
                if not relevant_exception:
                    return None

            return event

        import sentry_sdk
        import anki
        import aqt
        config = aqt.mw.addonManager.getConfig(__name__)
        user_id = config.get('baserow_config', {}).get('username', None)
        sentry_sdk.init(
            dsn="https://77f699b8026646db8770b3bf0a0c8f49@o968582.ingest.sentry.io/4505112135270400",
            traces_sample_rate=0, # no transactions
            release=f'anki-vocabai@{addon.version.ANKI_VOCABAI_VERSION}',
            before_send=sentry_filter,
        )
        sentry_sdk.set_user({"id": user_id})
        sentry_sdk.set_tag("anki_version", anki.version)        

    # initialize anki addon
    addon.initialize()