"""Modal de configuración de APIs — solo claves, sin elegir modelos."""
import streamlit as st

from ..ai_providers import probar_y_listar_proveedor, validar_proveedores_en_config
from ..api_config import (
    CONFIG_FILENAME,
    PROVEEDORES,
    cargar_config_desde_json,
    proveedor_listo,
    proveedores_configurados,
    serializar_config,
    sincronizar_widgets_modal,
)


def _reset_uploader() -> None:
    st.session_state["modal_upload_id"] = st.session_state.get("modal_upload_id", 0) + 1


def _importar_y_validar(raw: str) -> tuple[dict, list[str], list[dict]]:
    """Carga JSON, prueba todas las claves y sincroniza toggles (sin cerrar el modal)."""
    nueva, avisos = cargar_config_desde_json(raw)
    with st.spinner("Probando APIs importadas…"):
        informes = validar_proveedores_en_config(nueva)
    sincronizar_widgets_modal(nueva, forzar=True)
    return nueva, avisos, informes


def _persistir_desde_widgets(config: dict) -> None:
    """Guarda en api_config lo que hay en los widgets del modal."""
    for pid in PROVEEDORES:
        wkey = f"modal_key_{pid}"
        won = f"modal_on_{pid}"
        if wkey not in st.session_state and won not in st.session_state:
            continue
        prov = config["providers"][pid]
        if wkey in st.session_state:
            key = (st.session_state.get(wkey) or "").strip()
            if key:
                prov["api_key"] = key
            elif not key and st.session_state.get(wkey) == "":
                prov["api_key"] = ""
        if won in st.session_state:
            key = (prov.get("api_key") or "").strip()
            activo = st.session_state.get(won, False)
            prov["habilitado"] = bool(key) and activo


def _render_proveedores(config: dict) -> None:
    for pid, meta in PROVEEDORES.items():
        prov = config["providers"][pid]
        ok = proveedor_listo(config, pid)
        badge = "✓ activa" if ok else "sin configurar"

        st.markdown(f"**{meta['nombre']}** · *{badge}*")
        st.caption(meta["descripcion"])

        c1, c2 = st.columns([4, 1])
        with c1:
            st.text_input(
                "API key",
                type="password",
                key=f"modal_key_{pid}",
                label_visibility="collapsed",
                placeholder="Pega tu clave API…",
            )
        with c2:
            key = (st.session_state.get(f"modal_key_{pid}") or "").strip()
            probar = st.button("Probar", key=f"modal_test_{pid}", use_container_width=True, disabled=not key)

        test_ok_msg = None
        test_fallido = None
        if probar and key:
            estado, det, _ = probar_y_listar_proveedor(pid, key, config)
            if estado == "ok":
                prov["habilitado"] = True
                st.session_state[f"modal_on_{pid}"] = True
                test_ok_msg = det
            elif estado == "cuota":
                test_fallido = ("warning", det)
            else:
                test_fallido = ("error", det)

        st.toggle("Usar esta API", key=f"modal_on_{pid}")

        if test_ok_msg:
            st.success(f"✓ {test_ok_msg}")
        elif test_fallido:
            nivel, msg = test_fallido
            if nivel == "warning":
                st.warning(f"⚠ {msg}")
            else:
                st.error(f"⚠ {msg}")

        modelos_disp = prov.get("modelos_disponibles") or []
        if modelos_disp:
            with st.expander(
                f"{len(modelos_disp)} modelos disponibles",
                expanded=bool(probar and test_ok_msg),
            ):
                st.caption(", ".join(modelos_disp))

        key = (st.session_state.get(f"modal_key_{pid}") or "").strip()
        prov["api_key"] = key
        prov["habilitado"] = bool(key) and st.session_state.get(f"modal_on_{pid}", False)

        st.link_button("¿Dónde consigo la key?", meta["registro_url"])
        if meta["multimodal"]:
            st.caption("PDF e imágenes → requiere esta API.")
        st.divider()


def _render_seccion_json(config: dict) -> dict:
    """Bloque import/export JSON. Devuelve config actualizada."""
    st.markdown(
        '<p class="modal-intro">Registro <strong>gratis</strong>, sin tarjeta. '
        "Tus claves viven <strong>solo en esta sesión</strong>. "
        "Omnitest elige el modelo automáticamente.</p>",
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
<div class="modal-json-panel">
  <p class="modal-json-eyebrow">Configuración rápida</p>
  <p class="modal-json-title">Importar / exportar claves</p>
  <p class="modal-json-lead">
    Guarda tus API keys en <code>{CONFIG_FILENAME}</code> para no copiarlas a mano
    cada vez que abras la app. El archivo <strong>solo contiene tus claves</strong>;
    no se sube a ningún servidor.
  </p>
  <div class="modal-json-steps">
    <div class="modal-json-step">
      <span class="modal-json-step-num">1</span>
      <div class="modal-json-step-body">
        <p class="modal-json-step-title">Primera vez</p>
        <p class="modal-json-step-text">
          Pega las claves en cada proveedor, pulsa <strong>Probar</strong> y activa
          <strong>Usar esta API</strong>. Luego descarga el JSON y guárdalo en tu PC.
        </p>
      </div>
    </div>
    <div class="modal-json-step">
      <span class="modal-json-step-num">2</span>
      <div class="modal-json-step-body">
        <p class="modal-json-step-title">Siguientes veces</p>
        <p class="modal-json-step-text">
          Importa ese archivo con el botón de abajo. Omnitest restaurará las claves,
          las probará y activará las que funcionen.
        </p>
      </div>
    </div>
  </div>
</div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<p class="modal-json-actions-label">Acciones</p>', unsafe_allow_html=True)
    col_up, col_down = st.columns(2, gap="medium")
    with col_up:
        st.caption("Restaurar claves desde un archivo")
        upload_key = f"modal_upload_{st.session_state.get('modal_upload_id', 0)}"
        subido = st.file_uploader(
            "Importar JSON",
            type=["json"],
            key=upload_key,
            label_visibility="collapsed",
        )
        if subido:
            try:
                config, avisos, informes = _importar_y_validar(subido.read().decode("utf-8"))
                st.session_state["api_config"] = config
                n_ok = sum(1 for r in informes if r["ok"])
                st.session_state["api_import_msg"] = (
                    f"JSON importado — {n_ok} API(s) activa(s)."
                    if n_ok
                    else "JSON importado — revisa qué claves fallaron la prueba."
                )
                _reset_uploader()
                st.session_state["api_modal_reopen"] = True
                st.rerun()
            except ValueError as e:
                st.error(str(e))

    with col_down:
        st.caption("Guardar claves actuales en un archivo")
        json_out = serializar_config(st.session_state["api_config"])
        tiene = len(proveedores_configurados(st.session_state["api_config"])) > 0
        st.download_button(
            f"Descargar {CONFIG_FILENAME}",
            data=json_out,
            file_name=CONFIG_FILENAME,
            mime="application/json",
            use_container_width=True,
            disabled=not tiene,
        )

    return config


@st.dialog("APIs", width="large")
def api_modal() -> None:
    msg = (st.session_state.pop("api_import_msg", "") or "").strip()
    if msg:
        st.success(msg)

    config = st.session_state["api_config"]

    config = _render_seccion_json(config)
    sincronizar_widgets_modal(st.session_state["api_config"], forzar=bool(msg))

    st.divider()
    _render_proveedores(st.session_state["api_config"])
    _persistir_desde_widgets(st.session_state["api_config"])

    n = len(proveedores_configurados(st.session_state["api_config"]))
    if n:
        st.caption(f"{n} API(s) activa(s). El router elegirá la más eficiente en cada conversión.")
    else:
        st.info("Añade al menos una clave para usar el modo IA.")

    if st.button("Listo", type="primary", use_container_width=True):
        _persistir_desde_widgets(st.session_state["api_config"])
        st.rerun()
