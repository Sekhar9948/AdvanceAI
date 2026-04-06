import customtkinter as ctk
from .base_model_screen import BaseModelScreen
import os
import subprocess
import sys
import re


# ✅ Safe translator fallback
class DummyTranslator:
    def t(self, key):
        return key


class TextModelCard(ctk.CTkFrame):
    """A card component representing a text model with enhanced visuals"""
    def __init__(self, parent, title, description, model_type="text", callback=None, translator=None, **kwargs):
        self.translator = translator or DummyTranslator()
        self.t = self.translator.t

        super().__init__(
            parent,
            corner_radius=10,
            fg_color=("#2D2D2D", "#EFEFEF"),
            border_width=1,
            border_color=("#3F3F3F", "#DADADA"),
            **kwargs
        )

        self.title = title
        self.description = description
        self.model_type = model_type
        self.callback = callback

        self.grid_columnconfigure(0, weight=1)

        self._create_header()
        self._create_content()
        self._create_footer()

        self.bind("<Enter>", self._on_hover)
        self.bind("<Leave>", self._on_leave)

    def _create_header(self):
        self.header = ctk.CTkFrame(self, fg_color="transparent")
        self.header.grid(row=0, column=0, sticky="ew", padx=15, pady=(15, 5))
        self.header.grid_columnconfigure(0, weight=1)

        self.title_label = ctk.CTkLabel(
            self.header,
            text=self.title,
            font=ctk.CTkFont(family="Roboto", size=16, weight="bold"),
            anchor="w"
        )
        self.title_label.grid(row=0, column=0, sticky="w")

        self.tag = ctk.CTkLabel(
            self.header,
            text=self.t("text").upper(),
            font=ctk.CTkFont(family="Roboto", size=11),
            fg_color=("#1565C0", "#1976D2"),
            corner_radius=4,
            text_color="#FFFFFF",
            padx=8,
            pady=2
        )
        self.tag.grid(row=0, column=1, sticky="e")

    def _create_content(self):
        self.content = ctk.CTkFrame(self, fg_color="transparent")
        self.content.grid(row=1, column=0, sticky="nsew", padx=15, pady=5)

        self.desc_label = ctk.CTkLabel(
            self.content,
            text=self.description,
            font=ctk.CTkFont(family="Roboto", size=13),
            anchor="w",
            justify="left",
            wraplength=350
        )
        self.desc_label.pack(fill="both", expand=True)

    def _create_footer(self):
        self.footer = ctk.CTkFrame(self, fg_color="transparent")
        self.footer.grid(row=2, column=0, sticky="ew", padx=15, pady=(5, 15))
        self.footer.grid_columnconfigure(1, weight=1)

        self.try_button = ctk.CTkButton(
            self.footer,
            text=self.t("try_model"),
            font=ctk.CTkFont(family="Roboto", size=13),
            fg_color=("#1976D2", "#1565C0"),
            hover_color=("#1565C0", "#0D47A1"),
            corner_radius=6,
            height=30,
            command=self._on_try_clicked
        )
        self.try_button.grid(row=0, column=1, sticky="e")

        self.info_button = ctk.CTkButton(
            self.footer,
            text=self.t("learn_more"),
            font=ctk.CTkFont(family="Roboto", size=13),
            fg_color="transparent",
            hover_color=("#333333", "#E0E0E0"),
            corner_radius=6,
            height=30
        )
        self.info_button.grid(row=0, column=0, sticky="w")

    def _on_try_clicked(self):
        if callable(self.callback):
            self.callback(self.title)

    def _on_hover(self, event):
        self.configure(border_color=("#4F4F4F", "#BBBBBB"))

    def _on_leave(self, event):
        self.configure(border_color=("#3F3F3F", "#DADADA"))

    def refresh_ui(self):
        self.try_button.configure(text=self.t("try_model"))
        self.info_button.configure(text=self.t("learn_more"))


class TextModelsScreen(BaseModelScreen):
    def __init__(self, parent, theme_manager=None, translator=None):
        self.translator = translator or DummyTranslator()
        self.t = self.translator.t

        super().__init__(
            parent,
            theme_manager=theme_manager,
            title=self.t("text_models"),
            description=self.t("text_models_description")
        )

        self.add_text_models()
        self.show_model_preview(self.t("sentiment_analysis"))

    def add_text_models(self):
        self.add_model(
            title=self.t("sentiment_analysis"),
            description=self.t("sentiment_desc"),
            icon_path=None
        )

        self.add_model(
            title=self.t("ngram_model"),
            description=self.t("ngram_desc"),
            icon_path=None
        )

        self.add_model(
            title=self.t("language_classification"),
            description=self.t("language_classification_desc"),
            icon_path=None
        )

    def analyze_sentiment(self):
        text = self.sentiment_entry.get()

        if not text:
            self.result_label.configure(
                text=self.t("empty_input"),
                text_color="orange"
            )
            return

        words = re.findall(r'\b\w+\b', text.lower())

        positive_words = ["good", "great", "excellent", "amazing", "happy", "love"]
        negative_words = ["bad", "terrible", "awful", "hate"]

        pos_count = sum(1 for word in words if word in positive_words)
        neg_count = sum(1 for word in words if word in negative_words)

        if pos_count > neg_count:
            sentiment, color = self.t("positive"), "#4CAF50"
        elif neg_count > pos_count:
            sentiment, color = self.t("negative"), "#F44336"
        else:
            sentiment, color = self.t("neutral"), "#FFC107"

        self.result_label.configure(
            text=f"{self.t('sentiment')}: {sentiment}",
            text_color=color
        )

    def launch_language_classification_interface(self):
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            root_dir = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))

            model_path = os.path.join(
                root_dir,
                "tool_gui",
                "language_classification",
                "language_detection_main_gui.py"
            )

            if not os.path.exists(model_path):
                model_path = os.path.join(
                    os.getcwd(),
                    "tool_gui",
                    "language_classification",
                    "language_detection_main_gui.py"
                )

            subprocess.Popen(
                [sys.executable, model_path],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

        except Exception as e:
            print(self.t("error"), e)