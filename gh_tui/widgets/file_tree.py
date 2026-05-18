from __future__ import annotations

from textual.message import Message
from textual.widgets import Tree

from gh_tui.api.models import TreeEntry


class FileTree(Tree):
    """File tree sidebar with ASCII branch styling."""

    DEFAULT_CSS = """
    FileTree {
        width: 28;
        min-width: 22;
        height: 100%;
        border: none;
        border-right: solid #2a2a2a;
        background: #161616;
        padding: 0 1;
        color: #a0a0a0;
    }
    
    FileTree:focus {
        border-right: solid #d4a373;
        background: #181818;
    }
    
    FileTree > .tree--cursor {
        background: #2a2a2a;
    }
    
    FileTree > .tree--cursor:hover {
        background: #333333;
    }
    
    FileTree > .tree--highlight {
        background: transparent;
    }
    
    FileTree > .tree--guides {
        color: #3a3a3a;
    }
    
    FileTree > .tree--guides-selected {
        color: #d4a373;
    }
    
    FileTree > .tree--label {
        text-style: none;
    }
    
    FileTree > .tree--label-selected {
        color: #e0e0e0;
        text-style: bold;
    }
    """

    class EntrySelected(Message):
        """Posted when user selects a file or directory."""

        def __init__(self, path: str, entry_type: str) -> None:
            self.path = path
            self.entry_type = entry_type
            super().__init__()

    def load_root(self, entries: list[TreeEntry]) -> None:
        self.clear()
        self.root.set_label("[dim]─[/dim] [bold]/[/bold]")
        self.root.expand()
        self._add_entries(self.root, entries)

    def _add_entries(self, parent, entries: list[TreeEntry]) -> None:
        for entry in entries:
            icon = "▸ " if entry.entry_type == "dir" else "  "
            label = f"[dim]│[/dim] {icon}[bold]{entry.name}[/bold]" if entry.entry_type == "dir" else f"[dim]│[/dim]   {entry.name}"
            node = parent.add(label, data={"path": entry.path, "type": entry.entry_type})
            if entry.entry_type == "dir":
                node.allow_expand = True
                node.add_leaf("[dim]│   ⋮[/dim]", data={"path": entry.path, "type": "placeholder"})

    def add_children(self, dir_path: str, entries: list[TreeEntry]) -> None:
        node = self._find_node(dir_path)
        if node is None:
            return
        node.remove_children()
        self._add_entries(node, entries)
        node.expand()

    def _find_node(self, path: str):
        for node in self.root.walk_tree():
            data = node.data
            if data and data.get("path") == path and data.get("type") != "placeholder":
                return node
        return None

    def on_tree_node_expanded(self, event: Tree.NodeExpanded) -> None:
        data = event.node.data
        if not data or data.get("type") != "dir":
            return
        children = list(event.node.children)
        if len(children) == 1:
            child_data = children[0].data
            if child_data and child_data.get("type") == "placeholder":
                self.post_message(self.EntrySelected(data["path"], "dir"))

    def on_tree_node_selected(self, event: Tree.NodeSelected) -> None:
        data = event.node.data
        if not data or data.get("type") == "placeholder":
            return
        self.post_message(self.EntrySelected(data["path"], data["type"]))
