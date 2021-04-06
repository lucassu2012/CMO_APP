import numpy
import folium
import folium.plugins
from folium.elements import JSCSSMixin
from branca.element import MacroElement, Figure
from jinja2 import Template
import branca
import seaborn
import pandas
import geopandas
import pylab
from matplotlib.colors import is_color_like


# %% basemaps dict
basemaps = {'openstreetmap': dict(tiles='openstreetmap'),
            'google maps': dict(tiles='https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}',
                                attr='google',
                                subdomains=['mt0', 'mt1', 'mt2', 'mt3'],
                                name='google maps'),
            'google satellite': dict(tiles='http://{s}.google.com/vt/lyrs=s&x={x}&y={y}&z={z}',
                                     attr='google',
                                     subdomains=['mt0', 'mt1', 'mt2', 'mt3'],
                                     name='google satellite'),
            # 'google terrain': dict(tiles='https://mt1.google.com/vt/lyrs=p&x={x}&y={y}&z={z}',
            #                          attr='google',
            #                          name='google terrain'),
            # 'esri satellite': dict(tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
            #                          attr='esri',
            #                          name='esri satellite')
            }


# %% _modify_HeaderLegend function
def _modify_HeaderLegend(map_folium, layout=(1, 1), position=(0, 0)):
    n_row, n_col = layout
    i, j = position
    right = int((n_col - j - 1) * int(100 / n_col) + 1)
    bottom = int((n_row - i - 1) * int(100 / n_row) + 3)
    m_n = i * n_col + j
    layout_position = 'right: {}%;\n        bottom: {}%;'.format(right, bottom)

    # Header to Add
    head = f"""
    {{% macro header(this, kwargs) %}}
    <script src="https://code.jquery.com/ui/1.12.1/jquery-ui.js"></script>
    <script>$( function() {{
        $( ".maplegend{m_n}" ).draggable({{
            start: function (event, ui) {{
                $(this).css({{
                    right: "auto",
                    top: "auto",
                    bottom: "auto"
                }});
            }}
        }});
    }});
    </script>
    {{% endmacro %}}
    """
    # Add Header
    macro = branca.element.MacroElement()
    macro._template = branca.element.Template(head)
    map_folium.get_root().add_child(macro)
    # CSS to Add (on Header)
    css = f"""
    {{% macro header(this, kwargs) %}}
    <style type='text/css'>
      .maplegend{m_n} {{
        position: absolute;
        z-index:9999;
        background-color: rgba(255, 255, 255, 1);
        border-radius: 5px;
        border: 0px solid #bbb;
        padding: 10px;
        font-size:12px;
        {layout_position}
        opacity: 0.6;
      }}
      .maplegend{m_n} .legend-title {{
        text-align: left;
        margin-bottom: 5px;
        font-weight: bold;
        font-size: 90%;
        }}
      .maplegend{m_n} .legend-scale ul {{
        margin: 0;
        margin-bottom: 0px;
        padding: 0;
        float: left;
        list-style: none;
        }}
      .maplegend{m_n} .legend-scale ul li {{
        font-size: 80%;
        list-style: none;
        margin-left: 2px;
        line-height: 18px;
        margin-bottom: 2px;
        }}
      .maplegend{m_n} ul.legend-labels li span {{
        display: block;
        float: left;
        height: 16px;
        width: 30px;
        margin-right: 5px;
        margin-left: 2px;
        border: 0px solid #ccc;
        }}
      .maplegend{m_n} .legend-source {{
        font-size: 80%;
        color: #777;
        clear: both;
        }}
      .maplegend{m_n} a {{
        color: #777;
        }}
    </style>
    {{% endmacro %}}
    """
    # Add CSS (on Header)
    macro = branca.element.MacroElement()
    macro._template = branca.element.Template(css)
    map_folium.get_root().add_child(macro)
    return map_folium


# %% _add_CategoricalLegend function
def _add_CategoricalLegend(map_folium, title, color_by_label, layout=(1, 1), position=(0, 0), bin_decimal=0):
    n_row, n_col = layout
    i, j = position
    m_n = i * n_col + j

    body = f"""
    <div id='maplegend{m_n} {title}' class='maplegend{m_n}'>
        <div class='legend-title'>{title}</div>
        <div class='legend-scale'>
            <ul class='legend-labels'>"""
    # Loop Categories
    for label, color in color_by_label.items():
        _is_numeric = numpy.issubdtype(type(label), numpy.number)
        label_decimal = ("{:." + str(bin_decimal) + "f}").format(label) if _is_numeric is True else label
        body += f"""
                <li><span style='background:{color}'></span>{label_decimal}</li>"""
    body += """
            </ul>
        </div>
    </div>
    """
    # Add Body
    body = branca.element.Element(body)
    map_folium.get_root().html.add_child(body)
    return map_folium


# %% folium_color_categorical function
def folium_color_categorical(gdf, col, color_dict=None, palette_n='viridis'):
    # get all categorical values
    try:
        value_cat = sorted(gdf[col].dropna().unique())
    except:
        print('Something wrong with input gdf[col]')
        return
        # Create color dict
    if color_dict is None:
        # convert palette from str name to dict format
        if isinstance(palette_n, str):
            if is_color_like(palette_n):
                # palette_n = 'black'
                print('Input palette_n is a single matplotlib color.')
                color_pal = lambda x: palette_n
                return color_pal
            else:
                # palette_n = 'viridis'
                palette_n = {palette_n: len(value_cat)}

        if isinstance(palette_n, dict):
            # palette_n = {'Reds': 3, 'Blues': 3}
            if sum(palette_n.values()) >= len(value_cat):
                try:
                    color_palette = [seaborn.color_palette(p, n).as_hex() for p, n in palette_n.items()]
                    colors_cat = list(numpy.hstack(color_palette))
                    color_dict = dict(zip(value_cat, colors_cat))
                except:
                    print('Input palette_n is not a valid seaborn color palette.')
                    return
            else:
                print('palette_n total color number "{}" must be equal or larger than category number "{}"'.
                      format(sum(palette_n.values()), len(value_cat)))
                return
        else:
            print('Input palette_n must be "str" or "dict" format.')
            print('example: "blue", "Spectral" or {"Reds": 3, "Greens": 3}')
            return
    else:
        # color_dict = {'800 FDD - 10 MHz': 'Red', '925 FDD - 5 MHz': 'Yellow',
        #               '1800 FDD - 20 MHz': 'Blue', '2110 FDD - 20 MHz': 'Green',
        #               '2600 FDD - 20 MHz': 'Purple', 'Band 28 - 5 MHz': 'Black'}
        if not all(numpy.isin(value_cat, list(color_dict.keys()))):
            print('Some category is missing in color_dict input')
            return
        if not all([is_color_like(v) for v in color_dict.values()]):
            print('Some color-value is not a valid matplotlib color, '
                  'you can use "is_color_like" function to check')
            return
    # color function
    color_pal = lambda x: color_dict[x]  # color_pal('800 FDD - 10 MHz')
    return color_pal


# %% folium_color_linear function
def folium_color_linear(gdf, col, color_dict=None, palette_n='viridis'):
    if color_dict is None:
        if isinstance(palette_n, str):
            if is_color_like(palette_n):
                # palette_n = 'black'
                print('Input palette_n is a single color.')
                color_pal = lambda x: palette_n
                return color_pal
            else:
                # palette_n = 'viridis'
                try:
                    color_val = gdf[col].dropna().quantile([0, 0.05, 0.25, 0.5, 0.75, 0.95, 1.0]).to_list()
                    palette_n = {palette_n: color_val}
                except:
                    print('Something wrong with input gdf[col]')
                    return
        if isinstance(palette_n, dict):
            if len(palette_n.keys()) == 1:
                # palette_n = {'viridis': [1, 23, 29, 37, 100]}
                try:
                    # check whether input palette_n is palette colors or single color
                    color_val = list(palette_n.values())[0]
                    colors_linear = seaborn.color_palette(list(palette_n.keys())[0], len(color_val)).as_hex()
                except:
                    print('Input palette_n is not a valid seaborn color palette.')
            else:
                print('Input palette_n must be only one individual seaborn palette for linear colormap')
                return
        else:
            print('Input palette_n must be "str" or "dict" format.')
            print('example: "blue", "viridis" or {"viridis": [1, 23, 29, 37, 100]}')
            return
    else:
        if len(color_dict.keys()) < 2:
            print('Input colors from color_dict must be at least two colors')
            return
        if not all([is_color_like(c) for c in color_dict.keys()]):
            print('Some color-value is not a valid matplotlib color, '
                  'you can use "is_color_like" function to check')
            return
        # color_dict = {'Red': 16, 'Yellow': 29, 'Green': 47}
        color_val = list(color_dict.values())
        colors_linear = list(color_dict.keys())

    # color function
    color_pal = branca.colormap.LinearColormap(colors=colors_linear, index=color_val,
                                               vmin=color_val[0], vmax=color_val[-1])
    return color_pal


# %% folium_polygon function
def folium_polygon(gdf, col, color_pal, groups=True, tooltip_col=None, n_col=6,
                   weight=0.1, Opacity=0.9, fillOpacity=0.6, bin_decimal=0,
                   Legend=True, MousePosition=True, Search=None, MiniMap=True, Draw=False,
                   Fullscreen=False, LocateControl=False, Geocoder=False, MeasureControl=False):
    ## Part1 - DATA VALIDATION
    # check input data and col
    if isinstance(gdf, geopandas.GeoDataFrame):
        cols = gdf.columns.to_list()
        cols.remove('geometry') if 'geometry' in cols else None
        if col in cols:
            # visualize n_col=6 columns by default
            # col_select = list(set([col] + cols[:n_col]))
            col_select = cols[:n_col] if isinstance(n_col, int) else [cols[i] for i in n_col]
            col_select = col_select if col in col_select else [col] + col_select
        else:
            print('column "{}" cannot be found!!!'.format(col))
            return
    else:
        print('Input must be GeoDataFrame format')
        return

    # validate tooltip_col
    if tooltip_col is None: tooltip_col = col
    # if color_pal is branca linear function, which means the input is linear data type
    if isinstance(color_pal, branca.colormap.LinearColormap):
        color_val = list(
            dict.fromkeys([round(min(gdf[col].dropna()), 2)] + color_pal.index + [round(max(gdf[col].dropna()), 2)]))
        col_cut = pandas.cut(x=gdf[col].dropna(), bins=sorted(color_val),
                             right=True, include_lowest=True, precision=2).astype(str)
        color_label = {v: color_pal(v) for v in color_pal.index}
    else:
        color_val = sorted(gdf[col].dropna().unique())
        col_cut = col
        color_label = {v: color_pal(v) for v in color_val}
    ## Part2 - CREATE MAPS
    # base map and tile layers
    m = folium.Map(tiles='Cartodb Positron', control_scale=True)
    # add maps
    for _, val in basemaps.items():
        folium.TileLayer(**val).add_to(m)

    # Create Feature Group Layer, used for searching
    fg = folium.FeatureGroup(name=col).add_to(m)
    # Create Polygons layers by group of col_cut
    for group, df in gdf.groupby(col_cut):
        # gropu_name = col + " value : " + group
        gropu_name = "value: " + str(group) + " - samples: " + str(len(df))
        # style with color dict
        style = lambda x: {
            # 'color': 'black',
            'color': color_pal(x['properties'][col]),
            'weight': weight,
            'Opacity': Opacity,
            'fillColor': color_pal(x['properties'][col]),
            'fillOpacity': fillOpacity}
        highlight = lambda x: {
            'weight': weight * 2,
            'fillOpacity': fillOpacity + 0.3}
        # show group column as default tooltip value
        tooltip = folium.GeoJsonTooltip(
            fields=[tooltip_col],
            aliases=[tooltip_col.upper()],
        )
        # show n_col columns as popup
        popup = folium.GeoJsonPopup(
            fields=col_select,
            aliases=col_select,
            style=('background-color: transparent;'
                   'opacity: 0.2;'
                   'position: absolute;'
                   'font-size:10px;')
        )
        # create geojson layer and add it to subgroup
        g = folium.GeoJson(data=df,
                           name=gropu_name,
                           style_function=style,
                           highlight_function=highlight,
                           tooltip=tooltip,
                           popup=popup
                           )
        # must add subgroup to map
        if groups is True:
            folium.plugins.FeatureGroupSubGroup(fg, name=gropu_name, control=True).add_child(g).add_to(m)
        else:
            folium.plugins.FeatureGroupSubGroup(fg, name=gropu_name, control=False).add_child(g).add_to(m)

    ## Part3 - ADD PLUGINS
    if Fullscreen is True:
        folium.plugins.Fullscreen(position='topleft').add_to(m)
    if LocateControl is True:
        folium.plugins.LocateControl(auto_start=True,
                                     position='topleft').add_to(m)
    if Geocoder is True:
        folium.plugins.Geocoder(collapsed=True,
                                add_marker=False,
                                position='topleft').add_to(m)
    if Draw is True:
        folium.plugins.Draw(export=True,
                            position='topleft').add_to(m)
    if MeasureControl is True:
        folium.plugins.MeasureControl(position='topleft').add_to(m)
    if Search is not None:
        folium.plugins.Search(
            layer=fg,  # feature group name
            geom_type='Polygon',
            placeholder='Search by {}'.format(Search),
            collapsed=True,
            search_label=Search  # search column name
        ).add_to(m)
    if MiniMap is True:
        folium.plugins.MiniMap(tile_layer='Cartodb Positron',
                               width=150, height=150,
                               toggle_display=True,
                               position='bottomleft').add_to(m)
    if MousePosition is True:
        folium.plugins.MousePosition(position='topright',
                                     separator=' | ',
                                     prefix="LngLat: ",
                                     lat_formatter="function(num) {return L.Util.formatNum(num, 3) + ' º ';};",
                                     lng_formatter="function(num) {return L.Util.formatNum(num, 3) + ' º ';};"
                                     ).add_to(m)
    ## Part4 - LAYER CONTROL
    # Add LayerControl function
    folium.LayerControl().add_to(m)
    # Add Auto Extend function
    m.fit_bounds(m.get_bounds())
    # Add Map Legend
    if Legend is True:
        m = _modify_HeaderLegend(m)
        m = _add_CategoricalLegend(m, title=col, color_by_label=color_label, bin_decimal=bin_decimal)
    return m


# %% folium_point function
def folium_point(gdf, col, color_pal, groups=True, tooltip_col=None, n_col=6,
                 radius=100, weight=1, Opacity=1.0, fill=True, bin_decimal=0,
                 Legend=True, MousePosition=True, Search=None, MiniMap=True, Draw=False,
                 Fullscreen=False, LocateControl=False, Geocoder=False, MeasureControl=False):
    ## Part1 - DATA VALIDATION
    # check input data and col
    if isinstance(gdf, geopandas.GeoDataFrame):
        cols = gdf.columns.to_list()
        if col in cols:
            # visualize n_col=6 columns by default
            # col_select = list(set([col] + cols[:n_col]))
            col_select = cols[:n_col] if isinstance(n_col, int) else [cols[i] for i in n_col]
            col_select = col_select if col in col_select else [col] + col_select
        else:
            print('column "{}" cannot be found!!!'.format(col))
            return
    else:
        print('Input must be GeoDataFrame')
        return
    # validate tooltip_col
    if tooltip_col is None: tooltip_col = col
    # if color_pal is branca linear function, which means the input is linear data type
    if isinstance(color_pal, branca.colormap.LinearColormap):
        color_val = list(
            dict.fromkeys([round(min(gdf[col].dropna()), 2)] + color_pal.index + [round(max(gdf[col].dropna()), 2)]))
        col_cut = pandas.cut(x=gdf[col].dropna(), bins=sorted(color_val),
                             right=True, include_lowest=True, precision=2).astype(str)
        color_label = {v: color_pal(v) for v in color_pal.index}
    else:
        color_val = sorted(gdf[col].dropna().unique())
        col_cut = col
        color_label = {v: color_pal(v) for v in color_val}
    ## Part2 - CREATE MAPS
    # base map and tile layers
    m = folium.Map(tiles='Cartodb Positron', control_scale=True)
    # add maps
    for _, val in basemaps.items():
        folium.TileLayer(**val).add_to(m)
    # Create Feature Group Layer, used for searching
    fg = folium.FeatureGroup(name=col).add_to(m)
    table_class = 'table table-card-4 table-striped table-bordered table-hover table-condensed table-responsive'
    # Create Polygons layers by group of col_cut
    for group, df in gdf.groupby(col_cut):
        gropu_name = "value: " + str(group) + " - samples: " + str(len(df))
        # must add subgroup to map
        if groups is True:
            fgs = folium.plugins.FeatureGroupSubGroup(fg, name=gropu_name, control=True).add_to(m)
        else:
            fgs = folium.plugins.FeatureGroupSubGroup(fg, name=gropu_name, control=False).add_to(m)
        for i, data in df.iterrows():
            if (data[col] is not numpy.nan) & (data[col] is not None):
                folium.vector_layers.Circle(
                    location=data['geometry'].coords[:][0][::-1],
                    popup=folium.Popup(data[col_select].to_frame().to_html(header=False, classes=table_class)),
                    tooltip=data[tooltip_col],
                    stroke=True,
                    color=color_pal(data[col]),
                    radius=radius,
                    weight=weight,
                    opacity=Opacity,
                    # fillOpacity=1.0,
                    fill=fill,
                ).add_to(fgs)

    ## Part3 - ADD PLUGINS
    if Fullscreen is True:
        folium.plugins.Fullscreen(position='topleft').add_to(m)
    if LocateControl is True:
        folium.plugins.LocateControl(auto_start=True,
                                     position='topleft').add_to(m)
    if Geocoder is True:
        folium.plugins.Geocoder(collapsed=True,
                                add_marker=False,
                                position='topleft').add_to(m)
    if Draw is True:
        folium.plugins.Draw(export=True,
                            position='topleft').add_to(m)
    if MeasureControl is True:
        folium.plugins.MeasureControl(position='topleft').add_to(m)
    if Search is not None:
        folium.plugins.Search(
            layer=fg,
            geom_type='Point',
            placeholder='Search by {}'.format(Search),
            collapsed=True,
            # search_label=Search  # search column name
        ).add_to(m)
    if MiniMap is True:
        folium.plugins.MiniMap(tile_layer='Cartodb Positron',
                               width=150, height=150,
                               toggle_display=True,
                               position='bottomleft').add_to(m)
    if MousePosition is True:
        folium.plugins.MousePosition(position='topright',
                                     separator=' | ',
                                     prefix="LngLat: ",
                                     lat_formatter="function(num) {return L.Util.formatNum(num, 3) + ' º ';};",
                                     lng_formatter="function(num) {return L.Util.formatNum(num, 3) + ' º ';};"
                                     ).add_to(m)
    ## Part4 - LAYER CONTROL
    # Add LayerControl function
    folium.LayerControl().add_to(m)
    # Add Auto Extend function
    m.fit_bounds(m.get_bounds())
    # Add Map Legend
    if Legend is True:
        m = _modify_HeaderLegend(m)
        m = _add_CategoricalLegend(m, title=col, color_by_label=color_label, bin_decimal=bin_decimal)
    return m


# %% _select_col function
def _select_col(color_pal, gdf, col, n_col):
    # check input data and col
    if isinstance(gdf, geopandas.GeoDataFrame):
        cols = gdf.columns.to_list()
        if col in cols:
            col_select = cols[:n_col] if isinstance(n_col, int) else [cols[i] for i in n_col]
            col_select = col_select if col in col_select else [col] + col_select
            col_select.remove('geometry') if 'geometry' in col_select else None
        else:
            print('column "{}" cannot be found!!!'.format(col))
            return False
    else:
        print('Input must be GeoDataFrame')
        return False
    # if color_pal is branca linear function, which means the input is linear data type
    if isinstance(color_pal, branca.colormap.LinearColormap):
        color_val = list(
            dict.fromkeys([round(min(gdf[col].dropna()), 2)] + color_pal.index + [
                round(max(gdf[col].dropna()), 2)]))
        col_cut = pandas.cut(x=gdf[col].dropna(), bins=sorted(color_val),
                             right=True, include_lowest=True, precision=2).astype(str)
        color_label = {v: color_pal(v) for v in color_pal.index}
    else:
        color_val = sorted(gdf[col].dropna().unique())
        col_cut = col
        color_label = {v: color_pal(v) for v in color_val}
    return col_cut, col_select, color_label


# %% _add_group_point function
def _add_group_point(m, gdf, col, col_cut, col_select, color_pal, group_name, groups, tooltip_col, weight, opacity,
                     fill, fill_opacity, radius):
    table_class = 'table table-card-4 table-striped table-bordered table-hover table-condensed table-responsive'
    # overall group layer
    gr_name = (str(group_name) if group_name else str(col)) + ": All" + " | " + str(len(gdf))
    fg = folium.FeatureGroup(name=gr_name).add_to(m)
    # Create Polygons layers by group of col_cut
    for group, df in gdf.groupby(col_cut):
        l_name = (str(group_name) if group_name else str(col)) + ": " + str(group) + " | " + str(len(df))
        # must add subgroup to map
        if groups is True:
            fgs = folium.plugins.FeatureGroupSubGroup(fg, name=l_name, control=True).add_to(m)
        else:
            fgs = folium.plugins.FeatureGroupSubGroup(fg, name=l_name, control=False).add_to(m)
        # for each subgroup, add points
        for i, data in df.iterrows():
            if (data[col] is not numpy.nan) & (data[col] is not None):
                folium.vector_layers.Circle(
                    location=data['geometry'].coords[:][0][::-1],
                    popup=folium.Popup(data[col_select].to_frame().to_html(header=False, classes=table_class)),
                    tooltip=data[tooltip_col],
                    stroke=True,
                    color=color_pal(data[col]),
                    radius=radius,
                    weight=weight,
                    opacity=opacity,
                    fill_opacity=fill_opacity,
                    fill=fill,
                ).add_to(fgs)
    return m, fg


# %% _add_group_polygon function
def _add_group_polygon(m, gdf, col, col_cut, col_select, color_pal, group_name, groups, tooltip_col, weight, opacity,
                       fill, fill_opacity, color):
    # Create Feature Group Layer, used for searching
    g_name = (str(group_name) if group_name else str(col)) + ": All" + " | " + str(len(gdf))
    fg = folium.FeatureGroup(name=g_name).add_to(m)
    # Create Polygons layers by group of col_cut

    for group, df in gdf.groupby(col_cut):
        #
        l_name = (str(group_name) if group_name else str(col)) + ": " + str(group) + " | " + str(len(df))
        if groups is True:
            fgs = folium.plugins.FeatureGroupSubGroup(fg, name=l_name, control=True).add_to(m)
        else:
            fgs = folium.plugins.FeatureGroupSubGroup(fg, name=l_name, control=False).add_to(m)
        # create geojson layer and add it to subgroup
        folium.GeoJson(data=df,
                       name=l_name,
                       # style with color dict
                       style_function=lambda x: {
                           'color': color if is_color_like(color) else color_pal(x['properties'][col]),
                           'weight': weight,
                           'Opacity': opacity,
                           'fill': fill,
                           'fillColor': color_pal(x['properties'][col]),
                           'fillOpacity': fill_opacity
                       },
                       highlight_function=lambda x: {'weight': weight * 2,
                                                     'fillOpacity': fill_opacity + 0.3
                                                     },
                       # show group column as default tooltip value
                       tooltip=folium.GeoJsonTooltip(fields=[tooltip_col],
                                                     aliases=[tooltip_col.upper()],
                                                     ),
                       # show n_col columns as popup
                       popup=folium.GeoJsonPopup(fields=col_select,
                                                 aliases=col_select,
                                                 style=('background-color: transparent;'
                                                        'opacity: 0.2;'
                                                        'position: absolute;'
                                                        'font-size:10px;')
                                                 ),
                       ).add_to(fgs)
    return m, fg


# %% _add_layer function
def _add_layer(m, layout=(1, 1), position=(0, 0), gdf=None, col=None,
               group_name=None, groups=True, tooltip_col=None, n_col=6,
               color_mode='auto', color_dict=None, palette_n='viridis',
               weight=1.0, opacity=1.0, fill=True, fill_opacity=0.2,
               radius=100, color=None, bin_decimal=0,
               legend=True,
               ):
    if (gdf is None) or (col is None):
        print('"gdf" and "col" are both key parameters and must be presented as input')
        return False
    # check data type
    is_numeric = numpy.issubdtype(gdf[col].dtype, numpy.number)
    # color_pal function
    if (color_mode == 'linear') or (color_mode == 'auto' and is_numeric):
        color_pal = folium_color_linear(gdf=gdf,
                                        col=col,
                                        color_dict=color_dict,
                                        palette_n=palette_n
                                        )
    elif (color_mode == 'categorical') or (color_mode == 'auto' and not is_numeric):
        color_pal = folium_color_categorical(gdf=gdf,
                                             col=col,
                                             color_dict=color_dict,
                                             palette_n=palette_n
                                             )
    else:
        print('pls choose color_mode between "auto", "linear" and "categorical"')
        return False

    # output column information
    if _select_col(color_pal, gdf, col, n_col) is not False:
        col_cut, col_select, color_label = _select_col(color_pal, gdf, col, n_col)

    # validate tooltip_col
    if tooltip_col is None:
        tooltip_col = col

    # Add layer according to geometry type
    if all(gdf.geom_type.isin(['Point'])):
        m, fg = _add_group_point(m, gdf, col, col_cut, col_select, color_pal,
                                 group_name, groups, tooltip_col, weight, opacity, fill, fill_opacity, radius)
    if all(gdf.geom_type.isin(['MultiPolygon', 'Polygon'])):
        m, fg = _add_group_polygon(m, gdf, col, col_cut, col_select, color_pal,
                                   group_name, groups, tooltip_col, weight, opacity, fill, fill_opacity, color)

    # Add Map Legend
    if legend is True:
        m = _modify_HeaderLegend(m, layout=layout, position=position)
        m = _add_CategoricalLegend(m,
                                   title=group_name if group_name else col,
                                   color_by_label=color_label,
                                   layout=layout,
                                   position=position,
                                   bin_decimal=bin_decimal)
    return m, fg


# %% _add_plugins function
def _add_plugins(m,
                 Search=None, search_gdf=None, search_fg=None,
                 MousePosition=True, MiniMap=True, Draw=False,
                 Fullscreen=False, LocateControl=False, Geocoder=False, MeasureControl=False
                 ):
    if MousePosition is True:
        folium.plugins.MousePosition(position='topright',
                                     separator=' | ',
                                     prefix="LngLat: ",
                                     lat_formatter="function(num) {return L.Util.formatNum(num, 3) + ' º ';};",
                                     lng_formatter="function(num) {return L.Util.formatNum(num, 3) + ' º ';};"
                                     ).add_to(m)
    if Search is not None:
        if search_gdf.geom_type[0] == 'Point':
            geom_type = 'Point'
            search_fg = folium.GeoJson(search_gdf.to_json(),
                                       name='search',
                                       overlay=True,
                                       control=True,
                                       show=False
                                       ).add_to(m)
        else:
            geom_type = 'Polygon'
        folium.plugins.Search(
            layer=search_fg,  # feature group name
            geom_type=geom_type,
            placeholder='Search by {}'.format(Search[1]),
            collapsed=True,
            search_label=Search[1]  # search column name
        ).add_to(m)
    if MiniMap is True:
        folium.plugins.MiniMap(tile_layer='Cartodb Positron',
                               width=150, height=150,
                               toggle_display=True,
                               position='bottomleft').add_to(m)
    if Draw is True:
        folium.plugins.Draw(export=True,
                            position='topleft').add_to(m)
    if Fullscreen is True:
        folium.plugins.Fullscreen(position='topleft').add_to(m)
    if LocateControl is True:
        folium.plugins.LocateControl(auto_start=True,
                                     position='topleft').add_to(m)
    if Geocoder is True:
        folium.plugins.Geocoder(collapsed=True,
                                add_marker=False,
                                position='topleft').add_to(m)
    if MeasureControl is True:
        folium.plugins.MeasureControl(position='topleft').add_to(m)
    return m


# %% folium_plot function
def folium_plot(layer_list=None, gdf=None, col=None,
                group_name=None, groups=True, tooltip_col=None, n_col=6,
                color_mode='auto', color_dict=None, palette_n='viridis',
                weight=1.0, opacity=1.0, fill=True, fill_opacity=0.2,
                radius=100, color=None,
                legend=True, bin_decimal=0,
                MousePosition=True, Search=None, MiniMap=True, Draw=False,
                Fullscreen=False, LocateControl=False, Geocoder=False, MeasureControl=False
                ):
    # add base tile layers
    m = folium.Map(tiles='Cartodb Positron', control_scale=True)
    for _, val in basemaps.items():
        folium.TileLayer(**val).add_to(m)

    # add multiple data layers
    if isinstance(layer_list, list):
        for j, para_dict in enumerate(layer_list):
            if all(_ in para_dict.keys() for _ in ['gdf', 'col']):
                default_dict = {'group_name': group_name, 'groups': groups, 'tooltip_col': tooltip_col, 'n_col': n_col,
                                'color_mode': color_mode, 'color_dict': color_dict, 'palette_n': palette_n,
                                'weight': weight, 'opacity': opacity, 'fill': fill, 'fill_opacity': fill_opacity,
                                'radius': radius, 'color': color,
                                'legend': legend}
                default_dict.update(para_dict)
                m, fg = _add_layer(m, **default_dict)
                # search function
                if Search is None:
                    search_gdf, search_fg = None, None
                elif isinstance(Search, (tuple, list)) & (j == Search[0]):
                    search_gdf, search_fg = para_dict['gdf'], fg
            else:
                print('"gdf" and "col" are both key parameters and must be presented, ignore layer: %s' % j)
    # add single layers
    else:
        if isinstance(layer_list, dict):
            if all(_ in layer_list.keys() for _ in ['gdf', 'col']):
                default_dict = dict(group_name=group_name, groups=groups, tooltip_col=tooltip_col,
                                    n_col=n_col, color_mode=color_mode, color_dict=color_dict, palette_n=palette_n,
                                    weight=weight, opacity=opacity, fill=fill, fill_opacity=fill_opacity, radius=radius,
                                    color=color, legend=legend, bin_decimal=bin_decimal)
                default_dict.update(layer_list)
            else:
                print('"gdf" and "col" are both key parameters and must be presented, ignore the layer')
                # return False
        elif (layer_list is None) & (gdf is not None) & (col is not None):
            default_dict = dict(gdf=gdf, col=col, group_name=group_name, groups=groups, tooltip_col=tooltip_col,
                                n_col=n_col, color_mode=color_mode, color_dict=color_dict, palette_n=palette_n,
                                weight=weight, opacity=opacity, fill=fill, fill_opacity=fill_opacity, radius=radius,
                                color=color, legend=legend, bin_decimal=bin_decimal)
        else:
            print('either use "layer_list" or "gdf + col" as the key input, pls check')
            # return False

        # col = 'max_speed'
        m, fg = _add_layer(m, **default_dict)
        # search function
        if Search is None:
            search_gdf, search_fg = None, None
        else:
            search_gdf, search_fg = layer_list['gdf'], fg
    # add plugins
    m = _add_plugins(m,
                     Search=Search, search_gdf=search_gdf, search_fg=search_fg,
                     MousePosition=MousePosition, MiniMap=MiniMap, Draw=Draw,
                     Fullscreen=Fullscreen, LocateControl=LocateControl,
                     Geocoder=Geocoder, MeasureControl=MeasureControl
                     )
    # Add LayerControl function
    folium.LayerControl().add_to(m)
    # Add Auto Extend function
    m.fit_bounds(m.get_bounds())
    return m


# %% LayoutMap Class
class LayoutMap(JSCSSMixin, MacroElement):
    # import js
    default_js = [
        ('Leaflet.Sync',
         'https://cdn.jsdelivr.net/gh/jieter/Leaflet.Sync/L.Map.Sync.min.js')
    ]

    # inital class
    def __init__(self, location=None, layout=(1, 1), **kwargs):
        super(LayoutMap, self).__init__()
        # layout transform
        n_row, n_col = layout
        int_height, int_width = int(100 / n_row), int(100 / n_col)
        height, width = str(int(100 / n_row)) + '%', str(int(100 / n_col)) + '%'
        # create maps
        figure = Figure()
        maps = ['m' + str(i + 1) for i in range(n_row * n_col)]
        for i in range(n_row):
            for j in range(n_col):
                left = str(j * int_width) + '%'
                top = str(i * int_height) + '%'
                setattr(self, maps[i * n_col + j],
                        folium.Map(location=location, width=width, height=height,
                                   left=left, top=top,
                                   position='absolute', **kwargs).add_to(figure))
        # Important: add self to Figure last.
        figure.add_child(self)
        # list combination
        n = layout[0] * layout[1] + 1
        sync_list = []
        for i in range(1, n):
            for j in range(i + 1, n):
                sync_list += [(i, j), (j, i)]
        # sync part string
        sync = '\n            '.join(['{{{{ this.m{}.get_name() }}}}.sync({{{{ this.m{}.get_name() }}}});'.
                                     format(a, b) for a, b in sync_list])
        # update template
        self._template = Template(f"""
            {{% macro script(this, kwargs) %}}
                {sync}
            {{% endmacro %}}
        """)


# %% folium_layout Function
def folium_layout(layer_list=None, gdf=None, col=None, layout=(1, 1),
                  group_name=None, groups=True, tooltip_col=None, n_col=6,
                  color_mode='auto', color_dict=None, palette_n='viridis',
                  weight=1.0, opacity=1.0, fill=True, fill_opacity=0.2,
                  radius=100, color=None,
                  legend=True, bin_decimal=0
                  ):
    # multiple maps layout
    n_map = layout[0] * layout[1]
    if isinstance(layer_list, list) and n_map > 1:
        # base map with multiple sub-maps
        m = LayoutMap(layout=layout, tiles='Cartodb Positron', control_scale=True)
        maps = [m.__getattribute__('m' + str(i + 1)) for i in range(n_map)]
        # add each layers with for loop
        for k, (m_n, para_dict) in enumerate(zip(maps, layer_list)):
            position = divmod(k, layout[1])
            # add sub-map base layer
            for _, val in basemaps.items():
                folium.TileLayer(**val).add_to(m_n)
            # add data layers
            if all(_ in para_dict.keys() for _ in ['gdf', 'col']):
                # parameter update
                default_dict = dict(group_name=group_name, groups=groups, tooltip_col=tooltip_col, n_col=n_col,
                                    color_mode=color_mode, color_dict=color_dict, palette_n=palette_n, weight=weight,
                                    opacity=opacity, fill=fill, fill_opacity=fill_opacity, radius=radius, color=color,
                                    legend=legend, bin_decimal=bin_decimal)
                default_dict.update(para_dict)
                # add data layer
                _add_layer(m_n, layout, position, **default_dict)
                # Add LayerControl function
                folium.LayerControl().add_to(m_n)
                # Add Auto Extend function
                m_n.fit_bounds(m_n.get_bounds())
            else:
                print('"gdf" and "col" are both key parameters and must be presented, ignore %s' % m_n)
    # only one map as layout
    else:
        m = folium_plot(layer_list=layer_list, gdf=gdf, col=col,
                        group_name=group_name, groups=groups, tooltip_col=tooltip_col, n_col=n_col,
                        color_mode=color_mode, color_dict=color_dict, palette_n=palette_n, weight=weight,
                        opacity=opacity, fill=fill, fill_opacity=fill_opacity, radius=radius, color=color,
                        legend=legend, bin_decimal=bin_decimal
                        )
    return m
