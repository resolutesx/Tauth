import os
from kivy.storage.jsonstore import JsonStore
from kivy.utils import platform
from kivy.logger import Logger

# Request permissions on Android
if platform == "android":
    try:
        from android.permissions import request_permissions, Permission
        # For Android 11+, request MANAGE_EXTERNAL_STORAGE or use scoped storage
        request_permissions([
            Permission.READ_EXTERNAL_STORAGE,
            Permission.WRITE_EXTERNAL_STORAGE
        ])
    except ImportError:
        Logger.warning("ThemeManager: Android permissions module not available")

class ThemeManager:
    def __init__(self, app):
        self.app = app
        self.theme_store = None
        self.theme_pref_path = None
        self._init_theme_store()

    @property
    def user_data_dir(self):
        """
        Returns appropriate storage directory for each platform using modern methods.
        """
        plat = platform
        
        if plat == "android":
            return self._get_android_storage_path()
        elif plat == "ios":
            from os.path import expanduser
            return expanduser('~/Documents')
        else:
            return self.app.user_data_dir

    def _get_android_storage_path(self):
        """
        Get appropriate Android storage path using modern methods.
        Priority order:
        1. Internal app storage (no permissions needed)
        2. External app-specific storage (no permissions needed Android 10+)
        3. Fallback to internal storage
        """
        storage_paths = []
        
        try:
            # Method 1: Internal app storage (always available, no permissions)
            from android.storage import app_storage_path
            internal_path = app_storage_path()
            if internal_path:
                storage_paths.append(("Internal Storage", internal_path))
        except ImportError:
            Logger.warning("ModernThemeManager: android.storage not available")

        try:
            # Method 2: External app-specific storage (Android 10+, no permissions needed)
            from android.storage import external_storage_path
            external_path = external_storage_path()
            if external_path:
                storage_paths.append(("External App Storage", external_path))
        except ImportError:
            Logger.warning("ModernThemeManager: external_storage_path not available")

        try:
            # Method 3: Using Android context (requires python-for-android with proper setup)
            from jnius import autoclass
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            context = PythonActivity.mActivity
            
            # Internal files directory
            internal_files = context.getFilesDir()
            if internal_files:
                storage_paths.append(("Context Internal", internal_files.getAbsolutePath()))
            
            # External files directory (app-specific, no permissions needed)
            external_files = context.getExternalFilesDir(None)
            if external_files:
                storage_paths.append(("Context External", external_files.getAbsolutePath()))
                
        except Exception as e:
            Logger.info(f"ModernThemeManager: Context method not available: {e}")

        # Test each path and return the first writable one
        for name, path in storage_paths:
            if self._test_path_writable(path):
                Logger.info(f"ModernThemeManager: Using {name}: {path}")
                return path
        
        # Final fallback
        fallback = "/data/data/org.example.myapp/files"  # Replace with your package name
        Logger.warning(f"ModernThemeManager: Using fallback path: {fallback}")
        return fallback

    def _test_path_writable(self, path):
        """Test if a path is writable"""
        if not path or not os.path.exists(path):
            try:
                os.makedirs(path, exist_ok=True)
            except:
                return False
        
        try:
            test_file = os.path.join(path, ".write_test")
            with open(test_file, 'w') as f:
                f.write("test")
            os.remove(test_file)
            return True
        except:
            return False

    def _init_theme_store(self):
        """Initialize theme storage"""
        if self.theme_store is not None:
            return

        try:
            base_dir = self.user_data_dir
            Logger.info(f"ModernThemeManager: Using base directory: {base_dir}")
            
            # Ensure directory exists
            os.makedirs(base_dir, exist_ok=True)
            
            # Create theme preferences file path
            self.theme_pref_path = os.path.join(base_dir, "theme_prefs.json")
            
            # Initialize JsonStore
            self.theme_store = JsonStore(self.theme_pref_path)
            
            # Test write access
            self._test_write_access()
            
        except Exception as e:
            Logger.error(f"ModernThemeManager: Failed to initialize storage: {e}")
            self.theme_store = None

    def _test_write_access(self):
        """Test write access to theme store"""
        if not self.theme_store:
            return False
        
        try:
            test_key = '__write_test__'
            self.theme_store.put(test_key, test_value='write_test')
            
            if self.theme_store.exists(test_key):
                test_data = self.theme_store.get(test_key)
                if test_data.get('test_value') == 'write_test':
                    self.theme_store.delete(test_key)
                    Logger.info("ModernThemeManager: Write access confirmed")
                    return True
            
        except Exception as e:
            Logger.error(f"ModernThemeManager: Write test failed: {e}")
            
        return False

    def load_theme_prefs(self):
        """Load theme preferences"""
        if not self.theme_store:
            Logger.warning("ModernThemeManager: No storage available, using defaults")
            self._apply_default_theme()
            return

        try:
            if self.theme_store.exists('theme'):
                theme_data = self.theme_store.get('theme')
                self.app.theme_cls.primary_palette = theme_data.get('primary_palette', 'DeepOrange')
                self.app.theme_cls.theme_style = theme_data.get('theme_style', 'Light')
                Logger.info(f"ModernThemeManager: Loaded theme preferences")
            else:
                Logger.info("ModernThemeManager: No saved preferences, using defaults")
                self._apply_default_theme()
                self.save_theme_prefs()
                
        except Exception as e:
            Logger.error(f"ModernThemeManager: Error loading preferences: {e}")
            self._apply_default_theme()

    def save_theme_prefs(self):
        """Save theme preferences"""
        if not self.theme_store:
            Logger.warning("ModernThemeManager: No storage available, cannot save")
            return False

        try:
            self.theme_store.put(
                'theme',
                primary_palette=self.app.theme_cls.primary_palette,
                theme_style=self.app.theme_cls.theme_style
            )
            Logger.info("ModernThemeManager: Theme preferences saved successfully")
            return True
            
        except Exception as e:
            Logger.error(f"ModernThemeManager: Error saving preferences: {e}")
            return False

    def _apply_default_theme(self):
        """Apply default theme settings"""
        self.app.theme_cls.primary_palette = 'DeepOrange'
        self.app.theme_cls.theme_style = 'Light'

    def get_storage_debug_info(self):
        """Get detailed storage information for debugging"""
        info = {
            'platform': platform,
            'base_dir': None,
            'theme_path': self.theme_pref_path,
            'store_available': self.theme_store is not None,
            'android_methods': {}
        }
        
        try:
            info['base_dir'] = self.user_data_dir
        except Exception as e:
            info['base_dir_error'] = str(e)
        
        # Test Android-specific methods
        if platform == "android":
            # Test app_storage_path
            try:
                from android.storage import app_storage_path
                info['android_methods']['app_storage_path'] = app_storage_path()
            except Exception as e:
                info['android_methods']['app_storage_path_error'] = str(e)
            
            # Test external_storage_path
            try:
                from android.storage import external_storage_path
                info['android_methods']['external_storage_path'] = external_storage_path()
            except Exception as e:
                info['android_methods']['external_storage_path_error'] = str(e)
            
            # Test context methods
            try:
                from jnius import autoclass
                PythonActivity = autoclass('org.kivy.android.PythonActivity')
                context = PythonActivity.mActivity
                info['android_methods']['context_files_dir'] = context.getFilesDir().getAbsolutePath()
                external_files = context.getExternalFilesDir(None)
                if external_files:
                    info['android_methods']['context_external_files_dir'] = external_files.getAbsolutePath()
            except Exception as e:
                info['android_methods']['context_error'] = str(e)
        
        return info