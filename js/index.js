// ../js/index.js

window.deepText = {
    findInputByLabel(label) {
      const normalize = s => (s || "").trim().toLowerCase();
      const targetLabel = normalize(label);
  
      const inputs = [...document.querySelectorAll("input, textarea")]
        .filter(i => i.offsetParent !== null);
  
      // 1) aria-label / placeholder / label[for]
      for (const el of inputs) {
        if (normalize(el.getAttribute("aria-label")) === targetLabel) return el;
        if (normalize(el.placeholder) === targetLabel) return el;
  
        if (el.id) {
          const lbl = document.querySelector(`label[for="${el.id}"]`);
          if (lbl && normalize(lbl.innerText) === targetLabel) return el;
        }
      }
  
      // 2) Closest input to text on page
      const textElements = [...document.querySelectorAll("body *")]
        .filter(el => (el.innerText || "").toLowerCase().includes(targetLabel));
  
      function domDistance(a, b) {
        let d = 0, n = b;
        while (n && n !== document.body) {
          if (a.contains(n) || a === n) return d;
          n = n.parentElement;
          d++;
        }
        return Infinity;
      }
  
      let best = null, min = Infinity;
      for (const te of textElements) {
        for (const inp of inputs) {
          const dist = domDistance(te, inp);
          if (dist < min) {
            min = dist;
            best = inp;
          }
        }
      }
  
      return best;
    },
  
    toggleCheckbox(label, checked) {
      const t = label.toLowerCase();
      const boxes = [...document.querySelectorAll('input[type="checkbox"]')];
      for (const b of boxes) {
        const lbl = b.closest("label");
        if ((lbl?.innerText || "").toLowerCase().includes(t)) {
          b.checked = checked;
          b.dispatchEvent(new Event("change", { bubbles: true }));
          return true;
        }
      }
      return false;
    },
  
    selectRadio(option) {
      const t = option.toLowerCase().trim();
      const radios = [...document.querySelectorAll('input[type="radio"]')];
  
      function normalize(s) {
        return (s || "").toLowerCase().trim();
      }
  
      for (const r of radios) {
        if (normalize(r.value) === t) {
          (r.closest("label") || r).click();
          return true;
        }
      }
  
      for (const r of radios) {
        const lbl =
          r.closest("label") ||
          (r.id ? document.querySelector(`label[for="${r.id}"]`) : null);
  
        if (lbl && normalize(lbl.innerText).includes(t)) {
          lbl.click();
          return true;
        }
      }
      return false;
    },
  
    selectDropdown(label, option) {
      const tLabel = label.toLowerCase();
      const tOpt = option.toLowerCase();
  
      for (const sel of document.querySelectorAll("select")) {
        const lbl = sel.id
          ? document.querySelector(`label[for="${sel.id}"]`)
          : null;
  
        const meta = (
          sel.getAttribute("aria-label") ||
          sel.getAttribute("name") ||
          ""
        ).toLowerCase();
  
        if (meta.includes(tLabel) || lbl?.innerText.toLowerCase().includes(tLabel)) {
          const opt = [...sel.options].find(
            o =>
              o.textContent.toLowerCase().includes(tOpt) ||
              o.value.toLowerCase() === tOpt
          );
  
          if (opt) {
            sel.value = opt.value;
            sel.dispatchEvent(new Event("input", { bubbles: true }));
            sel.dispatchEvent(new Event("change", { bubbles: true }));
            return true;
          }
        }
      }
      return false;
    },
  
    clickByText(text) {
        const target = text.toLowerCase().trim();
      
        // Step 1: find elements containing the text
        const candidates = [...document.querySelectorAll("body *")].filter(el => {
          return (el.innerText || "").toLowerCase().trim() === target;
        });
      
        // Step 2: walk UP to nearest clickable ancestor
        for (const el of candidates) {
          const clickable = el.closest(
            "button, a, [role='button'], input[type='submit'], input[type='button']"
          );
      
          if (clickable && !clickable.disabled) {
            clickable.scrollIntoView({ block: "center" });
            clickable.click();
            return true;
          }
        }
      
        return false;
      }
      
      
  };
  