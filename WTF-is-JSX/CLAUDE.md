# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a minimal JSX implementation and demonstration repository. It contains a custom JSX renderer that converts JSX syntax to virtual DOM objects and renders them to the real DOM.

## Architecture

The core architecture consists of:

- **`myJSX.js`**: Main implementation file containing:
  - `h()` function: JSX pragma that converts JSX elements to virtual DOM objects
  - `render()` function: Converts virtual DOM objects to actual DOM elements
  - Demonstration code showing list rendering using the custom JSX implementation

- **`test.js`**: Test/example file demonstrating JSX usage with:
  - Array-to-list conversion functions
  - Virtual DOM to real DOM rendering examples
  - JSON representation of virtual DOM structures

## Key Implementation Details

- Uses `/** @jsx h */` pragma to configure JSX transpilation
- Virtual DOM structure: `{ nodeName, attributes, children }`
- Supports text nodes, element attributes, and nested children
- No build system or package.json - runs directly in browser

## Core Code Implementation

### JSX Pragma Function (`h`)

```javascript
function h(nodeName, attributes, ...args) {
    let children = args.length ? [].concat(...args) : null;
    return { nodeName, attributes, children};
}
```

This function serves as the JSX pragma that converts JSX elements to virtual DOM objects. When JSX is transpiled, `<div id="foo">Hello!</div>` becomes `h('div', {id:"foo"}, 'Hello')`.

### Virtual DOM Renderer

```javascript
function render(vnode) {
    // vnodeをtextノードに変更
    if (vnode.split) vnode.createTextNode(vnode)

    // vnodeのノード名を使用してDOM要素を作成
    let n = document.createElement(vnode.nodeName);

    // attributeを新しいノードに挿入
    let a = vnode.attributes || {};
    Object.keys(a).forEach( k => n.setAttribute(k, a[k]) );

    // renderして子ノードにアペンドする
    (vnode.children || []).forEach( c => n.appendChild(render(c)) )
}
```

The `render()` function recursively converts virtual DOM objects into real DOM elements.

### Example Usage Patterns

#### Basic List Rendering (myJSX.js)
```javascript
let items = ['foo', 'bar', 'baz'];

function item(text) {
    return h("li", null, text);
}

let list = render(
    h ("ul", null, items.map(item))
);

document.body.appendChild(list)
```

#### Complex JSX Structure (test.js)
```javascript
const ITEMS = 'hello there people'.split(' ');

let list = items => items.map( p => <li> {p} </li> );

let vdom = (
    <div id="foo">
        <p>Look, a simple JSX DOM renderer!</p>
        <ul>{ list(ITEMS) }</ul>
    </div>
);

let dom = render(vdom);
document.body.appendChild(dom);
```

#### Virtual DOM Inspection
```javascript
// Virtual DOM is just JSON objects
let json = JSON.stringify(vdom, null, '  ');
document.body.appendChild(
    render( <pre id="vdom">{ json }</pre> )
);
```

## Running the Code

This is a browser-only implementation with no build process:

1. Create an HTML file that includes both scripts:
```html
<!DOCTYPE html>
<html>
<head>
    <title>JSX Demo</title>
</head>
<body>
    <script src="myJSX.js"></script>
    <script src="test.js"></script>
</body>
</html>
```

2. Open the HTML file in a browser
3. No CLI commands or npm scripts available - this is a pure client-side demonstration

## Development Notes

- No testing framework or linting setup
- Code contains commented JSX examples alongside their `h()` function equivalents
- The `/** @jsx h */` pragma tells JSX transpilers to use the `h` function instead of `React.createElement`
- Virtual DOM structure is minimal: `{ nodeName, attributes, children }`
- Focuses on educational demonstration rather than production use
- Text nodes are handled by checking for `.split()` method (string detection)