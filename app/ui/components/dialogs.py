from pathlib import Path

from kivy.metrics import dp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDFlatButton, MDRaisedButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField

from app.utils.validation import validate_account_name, validate_totp_secret

class BaseDialog:
    def __init__(self, app):
        self.app = app
        self.dialog = None

    def show(self):
        if self.dialog:
            self.dialog.open()

    def close(self, *args):
        if self.dialog:
            self.dialog.dismiss()
            self.dialog = None

class AddAccountDialog(BaseDialog):
    def __init__(self, app, on_confirm_callback):
        super().__init__(app)
        self.on_confirm = on_confirm_callback
        self.name_field = None
        self.secret_field = None
        self._create_dialog()

    def _create_dialog(self):
        content = MDBoxLayout(
            orientation="vertical",
            spacing=dp(20),
            adaptive_height=True,
            padding=[dp(4), dp(8)]
        )

        self.name_field = MDTextField(
            hint_text="Account name (e.g., Google, GitHub)",
            required=True,
            helper_text_mode="on_error",
            helper_text="This field is required",
            line_color_focus=self.app.theme_cls.primary_color,
        )

        self.secret_field = MDTextField(
            hint_text="TOTP secret key",
            required=True,
            helper_text_mode="on_error",
            helper_text="Enter the secret key from your service",
            line_color_focus=self.app.theme_cls.primary_color,
        )

        content.add_widget(self.name_field)
        content.add_widget(self.secret_field)

        self.dialog = MDDialog(
            title="Add New Account",
            type="custom",
            content_cls=content,
            buttons=[
                MDFlatButton(
                    text="CANCEL",
                    theme_text_color="Custom",
                    text_color=self.app.theme_cls.disabled_hint_text_color,
                    on_release=self.close
                ),
                MDRaisedButton(
                    text="ADD",
                    md_bg_color=self.app.theme_cls.primary_color,
                    on_release=self.confirm
                ),
            ],
        )

    def confirm(self, instance):
        name = self.name_field.text.strip() if self.name_field and self.name_field.text else ""
        secret = self.secret_field.text.strip() if self.secret_field and self.secret_field.text else ""

        if not validate_account_name(name):
            if self.name_field:
                self.name_field.error = True
            return

        if not validate_totp_secret(secret):
            if self.secret_field:
                self.secret_field.error = True
            return

        self.on_confirm(name, secret)
        self.close()


class EditAccountDialog(BaseDialog):
    def __init__(self, app, account_name, on_confirm_callback):
        super().__init__(app)
        self.account_name = account_name
        self.on_confirm = on_confirm_callback
        self.secret_field = None
        self._create_dialog()

    def _create_dialog(self):
        content = MDBoxLayout(
            orientation="vertical",
            spacing=dp(20),
            adaptive_height=True,
            padding=[dp(4), dp(8)]
        )

        content.add_widget(MDLabel(
            text=f"Updating: {self.account_name}",
            theme_text_color="Secondary",
            font_style="Body2"
        ))

        self.secret_field = MDTextField(
            hint_text="New TOTP secret key",
            required=True,
            helper_text_mode="on_error",
            helper_text="Enter the new secret key",
            line_color_focus=self.app.theme_cls.primary_color,
        )

        content.add_widget(self.secret_field)

        self.dialog = MDDialog(
            title="Edit Account",
            type="custom",
            content_cls=content,
            buttons=[
                MDFlatButton(
                    text="CANCEL",
                    theme_text_color="Custom",
                    text_color=self.app.theme_cls.disabled_hint_text_color,
                    on_release=self.close
                ),
                MDRaisedButton(
                    text="UPDATE",
                    md_bg_color=self.app.theme_cls.primary_color,
                    on_release=self.confirm
                ),
            ],
        )

    def confirm(self, instance):
        if self.secret_field is None or not hasattr(self.secret_field, "text"):
            return  # Field not initialized, do nothing

        secret = self.secret_field.text.strip()

        if not validate_totp_secret(secret):
            if hasattr(self.secret_field, "error"):
                self.secret_field.error = True
            if hasattr(self.secret_field, "helper_text"):
                self.secret_field.helper_text = "Invalid TOTP secret"
            return

        self.on_confirm(self.account_name, secret)
        self.close()

class BackupDialog(BaseDialog):
    def __init__(self, app, directory, on_confirm_callback):
        super().__init__(app)
        self.directory = directory
        self.on_confirm = on_confirm_callback
        self.filename_field = None
        self.password_field = None
        self._create_dialog()

    def _create_dialog(self):
        content = MDBoxLayout(
            orientation="vertical",
            spacing=dp(20),
            adaptive_height=True,
            padding=[dp(4), dp(8)]
        )

        content.add_widget(MDLabel(
            text=f"Location: {self.directory}",
            theme_text_color="Secondary",
            font_style="Body2"
        ))

        self.filename_field = MDTextField(
            hint_text="Backup filename",
            text="authenticator_backup.bak",
            line_color_focus=self.app.theme_cls.primary_color,
        )

        self.password_field = MDTextField(
            hint_text="Backup password",
            password=True,
            required=True,
            helper_text_mode="on_error",
            helper_text="Password is required for encryption",
            line_color_focus=self.app.theme_cls.primary_color,
        )

        content.add_widget(self.filename_field)
        content.add_widget(self.password_field)

        self.dialog = MDDialog(
            title="Create Backup",
            type="custom",
            content_cls=content,
            buttons=[
                MDFlatButton(
                    text="CANCEL",
                    theme_text_color="Custom",
                    text_color=self.app.theme_cls.disabled_hint_text_color,
                    on_release=self.close
                ),
                MDRaisedButton(
                    text="BACKUP",
                    md_bg_color=self.app.theme_cls.primary_color,
                    on_release=self.confirm
                ),
            ],
        )

    def confirm(self, instance):
        if self.filename_field is not None:
            filename = self.filename_field.text.strip()
        else:
            filename = ""
        if self.password_field is not None:
            password = self.password_field.text.strip()
        else:
            password = ""

        if not password:
            if self.password_field is not None:
                self.password_field.error = True
            return

        if not filename:
            filename = "authenticator_backup.bak"

        self.on_confirm(self.directory, filename, password)
        self.close()

class RestoreDialog(BaseDialog):
    def __init__(self, app, filepath, on_confirm_callback):
        super().__init__(app)
        self.filepath = filepath
        self.on_confirm = on_confirm_callback
        self.password_field = None
        self._create_dialog()

    def _create_dialog(self):
        content = MDBoxLayout(
            orientation="vertical",
            spacing=dp(20),
            adaptive_height=True,
            padding=[dp(4), dp(8)]
        )

        content.add_widget(MDLabel(
            text=f"File: {Path(self.filepath).name}",
            theme_text_color="Secondary",
            font_style="Body2"
        ))

        self.password_field = MDTextField(
            hint_text="Backup password",
            password=True,
            required=True,
            helper_text_mode="on_error",
            helper_text="Enter the password used for encryption",
            line_color_focus=self.app.theme_cls.primary_color,
        )

        content.add_widget(self.password_field)

        self.dialog = MDDialog(
            title="Restore Backup",
            type="custom",
            content_cls=content,
            buttons=[
                MDFlatButton(
                    text="CANCEL",
                    theme_text_color="Custom",
                    text_color=self.app.theme_cls.disabled_hint_text_color,
                    on_release=self.close
                ),
                MDRaisedButton(
                    text="RESTORE",
                    md_bg_color=self.app.theme_cls.primary_color,
                    on_release=self.confirm
                ),
            ],
        )

    def confirm(self, instance):
        if self.password_field is None:
            return

        password = (self.password_field.text or "").strip()

        if not password:
            self.password_field.helper_text = "Password is required"
            self.password_field.helper_text_mode = "on_error"
            self.password_field.error = True
            return

        self.on_confirm(self.filepath, password)
        self.close()

class ErrorDialog(BaseDialog):
    def __init__(self, app, message):
        super().__init__(app)
        self.message = message
        self._create_dialog()

    def _create_dialog(self):
        self.dialog = MDDialog(
            title="Error",
            text=self.message,
            buttons=[
                MDRaisedButton(
                    text="OK",
                    md_bg_color=self.app.theme_cls.error_color,
                    on_release=self.close
                ),
            ],
        )

class ConfirmDialog(BaseDialog):
    def __init__(self, app, title, text, on_confirm_callback):
        super().__init__(app)
        self.title = title
        self.text = text
        self.on_confirm = on_confirm_callback
        self._create_dialog()

    def _create_dialog(self):
        self.dialog = MDDialog(
            title=self.title,
            text=self.text,
            buttons=[
                MDFlatButton(
                    text="CANCEL",
                    theme_text_color="Custom",
                    text_color=self.app.theme_cls.disabled_hint_text_color,
                    on_release=self.close
                ),
                MDRaisedButton(
                    text="CONFIRM",
                    md_bg_color=self.app.theme_cls.primary_color,
                    on_release=self.confirm
                ),
            ],
        )

    def confirm(self, instance):
        self.on_confirm()
        self.close()