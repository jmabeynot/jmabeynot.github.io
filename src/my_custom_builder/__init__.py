from pathlib import Path
from typing import List, Optional, Type

from docutils import nodes
from docutils.nodes import Element, Text
from docutils.parsers.rst import Directive, directives
from sphinx.application import Sphinx
from sphinx.util import logging
from sphinx.writers.html5 import HTML5Translator

logger = logging.getLogger(__name__)


class HTMLTranslator(HTML5Translator):
    def __init__(self, document, builder):
        super().__init__(document, builder)
        self.initial_header_level = 3

    def section_title_tags(self, node):
        start_tag, close_tag = super().section_title_tags(node)

        return f'<div class="section-title">{start_tag}', f"{close_tag}</div>"

    def visit_fixed_img_section(self, node):
        self.body.append(
            self.starttag(
                node,
                "div",
                CLASS="fixed-image",
                style=(
                    "background: linear-gradient(rgba(2, 2, 2, 0.5), "
                    "rgba(0, 0, 0, 0.8)), url(_static/img/how-to-begin.jpg) "
                    "center center fixed;"
                ),
            )
        )
        self.context.append("</div>\n")

    def depart_fixed_img_section(self, node):
        self.body.append(self.context.pop())

    def visit_section(self, node):
        if "how-to-begin" in node.attributes["ids"]:
            self.visit_fixed_img_section(node)
        self.section_level += 1
        self.body.append(self.starttag(node, "div", CLASS="container section clearfix"))
        self.context.append("</div>\n")

    def depart_section(self, node):
        if "how-to-begin" in node["ids"]:
            self.depart_fixed_img_section(node)
        self.section_level -= 1
        self.body.append(self.context.pop())

    # overwritten
    def visit_reference(self, node: Element) -> None:
        atts = {"class": "reference nav-link scrollto"}
        if node.get("internal") or "refuri" not in node:
            atts["class"] += " internal"
        else:
            atts["class"] += " external"
        if "refuri" in node:
            atts["href"] = node["refuri"] or "#"
            if self.settings.cloak_email_addresses and atts["href"].startswith(
                "mailto:"
            ):
                atts["href"] = self.cloak_mailto(atts["href"])
                self.in_mailto = True
        else:
            assert (
                "refid" in node
            ), 'References must have "refuri" or "refid" attribute.'
            atts["href"] = "#" + node["refid"]
        if not isinstance(node.parent, nodes.TextElement):
            assert len(node) == 1 and isinstance(node[0], nodes.image)
            atts["class"] += " image-reference"
        if "reftitle" in node:
            atts["title"] = node["reftitle"]
        if "target" in node:
            atts["target"] = node["target"]
        self.body.append(self.starttag(node, "a", **atts))

        if node.get("secnumber"):
            self.body.append(
                ("%s" + self.secnumber_suffix) % ".".join(map(str, node["secnumber"]))
            )

    def visit_image(self, node: Element) -> None:
        super().visit_image(node)
        img_tag = str(self.body[-1])
        sep = "/>"
        parts = img_tag.rsplit(sep, maxsplit=1)
        end = sep + parts.pop()
        parts.append(f'class="{node.get("class", "")}"')
        parts.append(end)

        self.body[-1] = " ".join(parts)


class MyDirective(Directive):
    def _add_parsed_text(
        self,
        text: str,
        containing_node: Element,
        new_node_type: Type = nodes.paragraph,
        classes: Optional[List[str]] = None,
    ):
        new_node = new_node_type()
        new_node.append(Text(str(text).strip()))
        self.state.nested_parse(new_node, 0, containing_node)

        if isinstance(classes, list):
            i = len(containing_node.children) - 1
            containing_node.children[i].attributes["classes"].extend(classes)


# ------------------------------------------------------- #


class RowDirective(MyDirective):

    has_content = True
    option_spec = {"class": str}

    def run(self):
        class_str = " ".join(
            ["row", "justify-content-md-center", self.options.get("class", "")]
        )
        row = div(CLASS=class_str.strip())
        self.state.nested_parse(self.content, self.content_offset, row)
        return [row]


# ------------------------------------------------------- #


class ColDirective(MyDirective):

    has_content = True
    option_spec = {"class": str}

    def run(self):
        col = div(CLASS=self.options.get("class", ""))
        self.state.nested_parse(self.content, self.content_offset, col)
        return [col]


# ------------------------------------------------------- #


# noinspection PyPep8Naming
class bs_icon_box(Element):
    pass


def visit_icon_box_node(self, node):
    self.body.append(self.starttag(node, "div", CLASS="icon-box"))
    self.context.append("</div>\n")


def depart_icon_box_node(self, node):
    self.body.append(self.context.pop())


# noinspection PyPep8Naming
class bs_icon(Element):
    pass


def visit_icon_node(self, node):
    node["class"] += " icon"
    self.body.append(self.starttag(node, "div", **dump_attrs(node)))
    self.context.append("</div>\n")


def depart_icon_node(self, node):
    self.body.append(self.context.pop())


# noinspection PyPep8Naming
class bs_icon_w_i(Element):
    pass


def visit_icon_w_i_node(self, node):
    self.body.append(self.starttag(node, "div", CLASS="icon"))
    self.context.append("</div>\n")

    self.body.append(self.starttag(node, "i", **dump_attrs(node)))
    self.context.append("</i>\n")


def depart_icon_w_i_node(self, node):
    self.body.append(self.context.pop())
    self.body.append(self.context.pop())


# noinspection PyPep8Naming
class bs_icon_box_subtitle(Element):
    pass


def visit_icon_box_subtitle_node(self, node):
    self.body.append(self.starttag(node, "h5", CLASS="title"))
    self.context.append("</h5>\n")


def depart_icon_box_subtitle_node(self, node):
    self.body.append(self.context.pop())


class IconBoxDirective(MyDirective):
    """
    .. bs-icon-box:: Title Here - Section Header (h4)
       :icon-class: bx bxl-dribbble

       Description text here should go in a <p class="description">
    """

    optional_arguments = 1
    final_argument_whitespace = True
    has_content = True
    option_spec = {
        "subtitle": str,
        "icon-class": str,
        "col-class": str,
    }

    def run(self):
        icon_box = bs_icon_box()

        if icon_class := self.options.get("icon-class"):
            icon = bs_icon(CLASS=icon_class)
            icon_box.append(icon)

        if self.arguments:
            title = h4(CLASS="title")
            title.extend([Text(("\n".join(self.arguments)).strip())])
            icon_box.append(title)

        if subtitle_text := self.options.get("subtitle"):
            subtitle = bs_icon_box_subtitle()
            subtitle.extend([Text(subtitle_text.strip())])
            icon_box.append(subtitle)

        if self.content:
            self._add_parsed_text(
                "\n".join(self.content), icon_box, classes=["description"]
            )

        if (col_class := self.options.get("col-class", "")) and icon_box.children:
            col = div(CLASS=col_class)
            col.extend([icon_box])

            return [col]

        return []


# ------------------------------------------------------- #


class TaglineDirective(MyDirective):

    has_content = True

    def run(self):
        p = nodes.paragraph(classes=["tagline"], text="\n".join(self.content))
        return [p]


# ------------------------------------------------------- #


def dump_attrs(node: Element) -> dict:
    return {k: v for k, v in node.attributes.items() if v and isinstance(v, str)}


# noinspection PyPep8Naming
class a(Element):
    pass


def visit_a_node(self, node):
    self.body.append(self.starttag(node, "a", **dump_attrs(node)))
    self.context.append("</a>")


def depart_a_node(self, node):
    self.body.append(self.context.pop())


# ------------------------------------------------------- #


# noinspection PyPep8Naming
class div(Element):
    pass


def visit_div_node(self, node):
    self.body.append(self.starttag(node, "div", **dump_attrs(node)))
    self.context.append("</div>")


def depart_div_node(self, node):
    self.body.append(self.context.pop())


class DivDirective(MyDirective):

    has_content = True
    optional_arguments = 1
    option_spec = {"class": str}

    def run(self):
        div_node = div(CLASS=self.options.get("class", ""))
        self.state.nested_parse(self.content, self.content_offset, div_node)
        return [div_node]


# ------------------------------------------------------- #


# noinspection PyPep8Naming
class span(Element):
    pass


def visit_span_node(self, node):
    self.body.append(self.starttag(node, "span", **dump_attrs(node)))
    self.context.append("</span>")


def depart_span_node(self, node):
    self.body.append(self.context.pop())


# ------------------------------------------------------- #


# noinspection PyPep8Naming
class ul(Element):
    pass


def visit_ul_node(self, node):
    self.body.append(self.starttag(node, "ul", **dump_attrs(node)))
    self.context.append("</ul>")


def depart_ul_node(self, node):
    self.body.append(self.context.pop())


# ------------------------------------------------------- #


# noinspection PyPep8Naming
class h3(Element):
    pass


def visit_h3_node(self, node):
    self.body.append(self.starttag(node, "h3", **dump_attrs(node)))
    self.context.append("</h3>\n")


def depart_h3_node(self, node):
    self.body.append(self.context.pop())


# ------------------------------------------------------- #


# noinspection PyPep8Naming
class h4(Element):
    pass


def visit_h4_node(self, node):
    self.body.append(self.starttag(node, "h4", **dump_attrs(node)))
    self.context.append("</h4>\n")


def depart_h4_node(self, node):
    self.body.append(self.context.pop())


# ------------------------------------------------------- #


# noinspection PyPep8Naming
class dolla(Element):
    pass


def visit_dolla_node(self, node):
    self.body.append(self.starttag(node, "sup", **dump_attrs(node)))
    self.body.append("$")
    self.context.append("</sup>")


def depart_dolla_node(self, node):
    self.body.append(self.context.pop())


# ------------------------------------------------------- #


class BoxDirective(MyDirective):

    has_content = True
    option_spec = {
        "class": str,
        "recommended": directives.flag,
        "badge": str,
        "service-pre": str,
        "service": str,
        "free": directives.flag,
        "price": directives.nonnegative_int,
        "per": str,
        "btn-text": str,
        "btn-href": str,
        "next-arrow-xs": str,
        "next-arrow-sm": str,
        "next-arrow-lg": str,
        "add-repeat-arrow": directives.flag,
    }

    def run(self):
        box_class = ("box w-100 " + self.options.get("class", "")).strip()
        if "recommended" in self.options:
            box_class += " recommended"
        box = div(CLASS=box_class)

        if next_arrow_cls := self.options.get("next-arrow-xs", "").strip():
            box.append(bs_icon(CLASS=f"box-next-arrow box-next-xs {next_arrow_cls}"))

        if next_arrow_sm_cls := self.options.get("next-arrow-sm", "").strip():
            box.append(bs_icon(CLASS=f"box-next-arrow box-next-sm {next_arrow_sm_cls}"))

        if next_arrow_lg_cls := self.options.get("next-arrow-lg", "").strip():
            box.append(bs_icon(CLASS=f"box-next-arrow box-next-lg {next_arrow_lg_cls}"))

        if "add-repeat-arrow" in self.options:
            box.append(bs_icon(CLASS="box-next-arrow bi bi-arrow-repeat"))

        if badge_text := self.options.get("badge"):
            self._add_parsed_text(badge_text, box, classes=["recommended-badge"])

        if srv_pre_text := self.options.get("service-pre", ""):
            self._add_parsed_text(srv_pre_text, box, classes=["pre-service"])

        service_text = self.options.get("service")
        assert service_text, "Box directive must have a service"
        service = h3()
        service.append(Text(service_text))
        box.append(service)

        if "free" in self.options:
            price = h4()
            price.append(Text("Free"))
            box.append(price)
        elif price_int := self.options.get("price"):
            price = h4()
            price.append(dolla())
            price.append(Text(f"{price_int}"))
            if per_text := self.options.get("per"):
                per = span()
                per.append(Text(f" / {per_text}"))
                price.append(per)
            box.append(price)
        else:
            box["class"] += " non-service"

        if self.content:
            self._add_parsed_text("\n".join(self.content), box)

        if btn_text := self.options.get("btn-text"):
            btn = div(CLASS="btn-wrap")
            if btn_href := self.options.get("btn-href"):
                a_node = a(href=btn_href, CLASS="btn-buy")
                a_node.append(Text(btn_text))
                btn.append(a_node)
            else:
                btn.append(Text(btn_text))
            box.append(btn)

        return [box]


# ------------------------------------------------------- #


class ListGroupDirective(MyDirective):

    has_content = True
    option_spec = {"class": str}

    def run(self):
        class_str = " ".join(["list-group", self.options.get("class", "")])
        list_group = div(CLASS=class_str.strip())
        self.state.nested_parse(self.content, self.content_offset, list_group)
        return [list_group]


# ------------------------------------------------------- #


# noinspection PyPep8Naming
class ListGroupItemDirective(MyDirective):

    optional_arguments = 1
    has_content = True
    option_spec = {
        "icon-class": str,
        "href": str,
    }
    final_argument_whitespace = True

    def run(self):
        item = div(CLASS="list-group-item list-group-item-action py-3 d-flex")
        children = []

        if icon_class := self.options.get("icon-class"):
            icon = bs_icon(CLASS=icon_class)
            children.append(icon)

        if (content := self.content) or self.arguments:
            cont = nodes.container()

            if title_text := self.arguments[0]:
                self._add_parsed_text(
                    title_text, cont, classes=["mb-0", "list-group-item-title"]
                )

            if content:
                self._add_parsed_text(
                    "\n".join(content), cont, classes=["mb-0", "opacity-75"]
                )

            children.append(cont)

        if children:
            if href := self.options.get("href"):
                a_node = a(href=href, CLASS="scrollto d-flex")
                a_node.extend(children)
                item.append(a_node)
                return [item]
            else:
                item.extend(children)
                return [item]

        return []


# ------------------------------------------------------- #


class CarouselDirective(MyDirective):

    has_content = False
    option_spec = {
        "id": directives.class_option,
        "class": str,
        "image-dir": directives.path,
        "images": str,
    }

    def run(self):
        carousel = div(CLASS="carousel-inner")

        if not (img_dir := self.options.get("image-dir")):
            raise ValueError("You must supply an image dir for a carousel")
        img_dir = Path(img_dir)

        for i, img_src in enumerate(self.options.get("images", "").split()):
            item = div(CLASS=f"carousel-item{' active' if i == 0 else ''}")
            item.append(
                nodes.image(CLASS="d-block rounded w-100", uri=f"{(img_dir / img_src)}")
            )
            carousel.append(item)

        class_str = " ".join(
            ["carousel", "carousel-fade", "slide", self.options.get("class", "")]
        )
        carousel_wrapper = div(
            CLASS=class_str.strip(),
            IDS=self.options.get("id", []),
            **{"data-bs-ride": "carousel"},
        )
        carousel_wrapper.append(carousel)
        return [carousel_wrapper]


# ------------------------------------------------------- #


class AccordianListDirective(MyDirective):

    has_content = True

    def run(self):
        accordion = div(CLASS="accordion")
        ulist = ul(CLASS="accordion-list")
        self.state.nested_parse(self.content, self.content_offset, ulist)
        accordion.append(ulist)
        return [accordion]


# ------------------------------------------------------- #


class AccordianItemDirective(MyDirective):

    required_arguments = 1
    final_argument_whitespace = True
    has_content = True

    def run(self):
        assert self.arguments
        item = nodes.list_item()
        item_id = f"accordion-item-{self.state.document.settings.env.new_serialno('accordion'):d}"
        title_div = div(
            CLASS="accordion-item collapsed",
            **{
                "data-bs-toggle": "collapse",
                "aria-expanded": "false",
                "href": f"#{item_id}",
            },
        )
        title_div.extend(
            [
                bs_icon_w_i(CLASS="bi bi-chevron-down icon-show"),
                bs_icon_w_i(CLASS="bi bi-chevron-up icon-close"),
                Text((" ".join(self.arguments)).strip()),
            ]
        )
        item.append(title_div)

        contents_div = div(
            ids=[item_id],
            CLASS="collapse",
            **{"data-bs-parent": ".accordion-list"},
        )
        self.state.nested_parse(self.content, self.content_offset, contents_div)
        item.append(contents_div)

        return [item]


# ------------------------------------------------------- #


class CTADirective(MyDirective):

    required_arguments = 1
    final_argument_whitespace = True
    option_spec = {
        "href": str,
    }

    def run(self):
        href = self.options.get("href")
        assert href, "CTA button must have an href option"
        a_node = a(href=href, CLASS="cta-btn scrollto")
        a_node.append(Text((" ".join(self.arguments)).strip()))

        wrapper = div(CLASS="text-center")
        wrapper.append(a_node)

        return [wrapper]


# ------------------------------------------------------- #


def setup(app: Sphinx):
    app.set_translator("html", HTMLTranslator)

    # Basic body elements
    app.add_node(a, html=(visit_a_node, depart_a_node))
    app.add_node(div, html=(visit_div_node, depart_div_node))
    app.add_node(span, html=(visit_span_node, depart_span_node))
    app.add_node(ul, html=(visit_ul_node, depart_ul_node))
    app.add_node(h3, html=(visit_h3_node, depart_h3_node))
    app.add_node(h4, html=(visit_h4_node, depart_h4_node))

    # Div directive
    app.add_directive("div", DivDirective)

    # Row directive
    app.add_directive("bs-row", RowDirective)

    # Col directive
    app.add_directive("bs-col", ColDirective)

    # Icon Box directive
    app.add_node(bs_icon_box, html=(visit_icon_box_node, depart_icon_box_node))
    app.add_node(bs_icon, html=(visit_icon_node, depart_icon_node))
    app.add_node(bs_icon_w_i, html=(visit_icon_w_i_node, depart_icon_w_i_node))
    app.add_node(
        bs_icon_box_subtitle,
        html=(visit_icon_box_subtitle_node, depart_icon_box_subtitle_node),
    )
    app.add_directive("bs-icon-box", IconBoxDirective)

    # Tagline directive
    app.add_directive("tagline", TaglineDirective)

    # List group directive
    app.add_directive("list-group", ListGroupDirective)

    # List group item directive
    app.add_directive("list-group-item", ListGroupItemDirective)

    # Box node
    app.add_directive("bs-box", BoxDirective)

    # Dolla
    app.add_node(dolla, html=(visit_dolla_node, depart_dolla_node))

    # Carousel directive
    app.add_directive("bs-carousel", CarouselDirective)

    # Accordion directives
    app.add_directive("bs-accordion", AccordianListDirective)
    app.add_directive("bs-accordion-item", AccordianItemDirective)

    # CTA directive
    app.add_directive("bs-cta", CTADirective)
