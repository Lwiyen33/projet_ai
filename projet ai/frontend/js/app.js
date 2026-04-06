(function () {
  var tbody = document.getElementById("tbody-products");
  var modelWarning = document.getElementById("model-warning");
  var globalMsg = document.getElementById("global-msg");
  var formAdd = document.getElementById("form-add");
  var formPredict = document.getElementById("form-predict");
  var resultEl = document.getElementById("result");
  var errorPredict = document.getElementById("error-predict");
  var qtyValue = document.getElementById("qty-value");
  var btnSubmit = document.getElementById("btn-submit");
  var dashCount = document.getElementById("dash-count");
  var dashStock = document.getElementById("dash-stock");
  var dashModel = document.getElementById("dash-model");

  function show(el, on) {
    el.classList.toggle("hidden", !on);
  }

  function flash(msg, isError) {
    globalMsg.textContent = msg;
    globalMsg.classList.toggle("msg--error", !!isError);
    show(globalMsg, true);
    window.setTimeout(function () {
      show(globalMsg, false);
    }, 4200);
  }

  function updateDashboard(products) {
    var list = products || [];
    var n = list.length;
    var total = 0;
    for (var i = 0; i < n; i++) {
      total += Number(list[i].stock) || 0;
    }
    dashCount.textContent = String(n);
    dashStock.textContent = String(total);
  }

  function setModelBadge(ok) {
    if (!dashModel) return;
    dashModel.textContent = ok ? "Prêt" : "Indisponible";
    dashModel.classList.toggle("is-off", !ok);
  }

  function loadProducts() {
    fetch("/api/products")
      .then(function (r) {
        return r.json();
      })
      .then(function (data) {
        if (!data.ok) {
          tbody.innerHTML =
            '<tr><td colspan="6" class="cell-empty">Erreur de chargement.</td></tr>';
          updateDashboard([]);
          return;
        }
        var products = data.products || [];
        updateDashboard(products);
        renderRows(products);
      })
      .catch(function () {
        tbody.innerHTML =
          '<tr><td colspan="6" class="cell-empty">Serveur injoignable.</td></tr>';
        updateDashboard([]);
      });
  }

  function renderRows(products) {
    if (!products.length) {
      tbody.innerHTML =
        '<tr><td colspan="6" class="cell-empty">Aucun produit. Utilisez le formulaire ci-dessous.</td></tr>';
      return;
    }
    tbody.innerHTML = "";
    products.forEach(function (p) {
      var tr = document.createElement("tr");
      tr.innerHTML =
        "<td>" +
        escapeHtml(p.name) +
        "</td>" +
        "<td>" +
        escapeHtml(p.category) +
        "</td>" +
        '<td><input type="number" class="input-inline" min="0" step="1" data-id="' +
        p.id +
        '" value="' +
        p.stock +
        '" aria-label="Stock ' +
        escapeHtml(p.name) +
        '"></td>' +
        "<td>" +
        p.avg_weekly_sales +
        "</td>" +
        "<td>" +
        p.lead_time_days +
        "</td>" +
        '<td class="cell-actions">' +
        '<button type="button" class="btn-inline" data-action="save" data-id="' +
        p.id +
        '">Stock</button> ' +
        '<button type="button" class="btn-inline btn-inline--accent" data-action="ia" data-id="' +
        p.id +
        '">IA</button> ' +
        '<button type="button" class="btn-inline btn-inline--danger" data-action="del" data-id="' +
        p.id +
        '">×</button>' +
        "</td>";
      tbody.appendChild(tr);
    });

    tbody.querySelectorAll('button[data-action="save"]').forEach(function (btn) {
      btn.addEventListener("click", function () {
        var id = Number(btn.getAttribute("data-id"));
        var inp = tbody.querySelector('input[data-id="' + id + '"]');
        if (!inp) return;
        patchProduct(id, { stock: Number(inp.value) });
      });
    });
    tbody.querySelectorAll('button[data-action="ia"]').forEach(function (btn) {
      btn.addEventListener("click", function () {
        suggestIa(Number(btn.getAttribute("data-id")));
      });
    });
    tbody.querySelectorAll('button[data-action="del"]').forEach(function (btn) {
      btn.addEventListener("click", function () {
        if (!window.confirm("Supprimer ce produit ?")) return;
        deleteProduct(Number(btn.getAttribute("data-id")));
      });
    });
  }

  function escapeHtml(s) {
    var d = document.createElement("div");
    d.textContent = s;
    return d.innerHTML;
  }

  function patchProduct(id, body) {
    fetch("/api/products/" + id, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    })
      .then(function (r) {
        return r.json().then(function (d) {
          return { ok: r.ok, d: d };
        });
      })
      .then(function (res) {
        if (res.d.ok) {
          flash("Stock enregistré.", false);
          loadProducts();
        } else {
          flash(res.d.error || "Erreur", true);
        }
      })
      .catch(function () {
        flash("Erreur réseau.", true);
      });
  }

  function suggestIa(id) {
    fetch("/api/products/" + id + "/suggest", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({}),
    })
      .then(function (r) {
        return r.json().then(function (d) {
          return { ok: r.ok, d: d };
        });
      })
      .then(function (res) {
        if (res.d.ok) {
          flash(
            "IA : " + res.d.quantity + " u. (mois " + res.d.month_used + ")",
            false
          );
        } else {
          flash(res.d.error || "Erreur IA", true);
        }
      })
      .catch(function () {
        flash("Erreur réseau.", true);
      });
  }

  function deleteProduct(id) {
    fetch("/api/products/" + id, { method: "DELETE" })
      .then(function (r) {
        return r.json().then(function (d) {
          return { ok: r.ok, d: d };
        });
      })
      .then(function (res) {
        if (res.d.ok) {
          flash("Produit supprimé.", false);
          loadProducts();
        } else {
          flash(res.d.error || "Erreur", true);
        }
      })
      .catch(function () {
        flash("Erreur réseau.", true);
      });
  }

  formAdd.addEventListener("submit", function (e) {
    e.preventDefault();
    var payload = {
      name: document.getElementById("add-name").value,
      category: document.getElementById("add-category").value,
      stock: Number(document.getElementById("add-stock").value),
      avg_weekly_sales: Number(document.getElementById("add-sales").value),
      lead_time_days: Number(document.getElementById("add-lead").value),
    };
    fetch("/api/products", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    })
      .then(function (r) {
        return r.json().then(function (d) {
          return { ok: r.ok, d: d };
        });
      })
      .then(function (res) {
        if (res.d.ok) {
          flash("Produit ajouté.", false);
          formAdd.reset();
          document.getElementById("add-stock").value = "0";
          document.getElementById("add-sales").value = "10";
          document.getElementById("add-lead").value = "14";
          loadProducts();
        } else {
          flash(res.d.error || "Erreur", true);
        }
      })
      .catch(function () {
        flash("Erreur réseau.", true);
      });
  });

  fetch("/api/health")
    .then(function (r) {
      return r.json();
    })
    .then(function (data) {
      var ok = !!data.model_ok;
      setModelBadge(ok);
      if (!ok) {
        modelWarning.textContent =
          "Modèle IA absent : exécutez python scripts/train_model.py";
        show(modelWarning, true);
      }
    })
    .catch(function () {
      setModelBadge(false);
    });

  (function setMonthDefault() {
    var m = document.getElementById("month");
    if (m) m.value = String(new Date().getMonth() + 1);
  })();

  loadProducts();

  formPredict.addEventListener("submit", function (e) {
    e.preventDefault();
    show(errorPredict, false);
    show(resultEl, false);
    var payload = {
      category: document.getElementById("category").value,
      current_stock: Number(document.getElementById("current_stock").value),
      avg_weekly_sales: Number(document.getElementById("avg_weekly_sales").value),
      lead_time_days: Number(document.getElementById("lead_time_days").value),
      month: Number(document.getElementById("month").value),
    };
    btnSubmit.disabled = true;
    btnSubmit.textContent = "…";
    fetch("/api/predict", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    })
      .then(function (r) {
        return r.json().then(function (data) {
          return { ok: r.ok, data: data };
        });
      })
      .then(function (res) {
        if (res.data.ok) {
          qtyValue.textContent = String(res.data.quantity);
          show(resultEl, true);
        } else {
          errorPredict.textContent = res.data.error || "Erreur";
          show(errorPredict, true);
        }
      })
      .catch(function () {
        errorPredict.textContent = "Serveur injoignable.";
        show(errorPredict, true);
      })
      .finally(function () {
        btnSubmit.disabled = false;
        btnSubmit.textContent = "Calculer";
      });
  });
})();
