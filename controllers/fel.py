# -*- coding: utf-8 -*-
import xml.etree.ElementTree as ET
import json, requests
import base64
import random
import io
from datetime import datetime

from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)

class controllerfel:
    def genxml(self,tipo):

        dicGTDocumento = {
            'xmlns:ds': "http://www.w3.org/2000/09/xmldsig#",
            'xmlns:dte': "http://www.sat.gob.gt/dte/fel/0.2.0",
            'xmlns:xsi': "http://www.w3.org/2001/XMLSchema-instance",
            'Version': "0.1",
            'xsi:schemaLocation': "http://www.sat.gob.gt/dte/fel/0.1.0"
        }
        dicSAT = {
            'ClaseDocumento': "dte"
        }

        dicDTE = {
            'ID': "DatosCertificados"
        }

        dicDatosEmision = {
            'ID': "DatosEmision"
        }


        fechafel = str(self.date)+"T"+str(self.create_date.strftime("%H:%M:%S"))+"-06:00"

        dicDatosGenerales = {
            'CodigoMoneda': "GTQ",
            'FechaHoraEmision' : fechafel,
            'Tipo': tipo
        }

        dicEmisor = {
            'AfiliacionIVA': "GEN",
            'CodigoEstablecimiento': self.env.company.fel_codigo_establecimiento,
            'CorreoEmisor': self.env.company.fel_correo_emisor,
            'NITEmisor': self.env.company.fel_nit_emisor,
            'NombreComercial': self.env.company.fel_nombre_Comercial,
            'NombreEmisor': self.env.company.fel_nombre_emisor
        }

        # dicEmisor = {
        #     'AfiliacionIVA': "GEN",
        #     'CodigoEstablecimiento': "1",
        #     'CorreoEmisor': "cleanfactoryvijusa@hotmail.com",
        #     'NITEmisor': "2459413K",
        #     'NombreComercial': "Rosa Victoria Rosado Lara de Estrada",
        #     'NombreEmisor': "Rosa Victoria Rosado Lara de Estrada"
        # }

        if (tipo == 'NCRE'):
            if (round(abs(self.amount_total_signed), 2) > 2500) and (self.partner_id.vat == 'CF') and (str(self.fel_fecha) > '2023-01-15)'):
                if not self.partner_id.ref:
                    raise ValidationError('Para este tipo de factura debe especificar un CUI en el campo "Referencia" del cliente, en la pestaña "Venta y Compra"')

                dicReceptor = {
                    'CorreoReceptor': "",
                    'IDReceptor': self.partner_id.ref,
                    'NombreReceptor': self.partner_id.fel_nombre_sat,
                    'TipoEspecial': 'CUI'
                }
            else:
                if not self.partner_id.vat:
                    raise ValidationError('Para poder facturar debe especificar un Nit, o bien especificar CF')

                dicReceptor = {
                    'CorreoReceptor': "",
                    'IDReceptor': self.partner_id.vat,
                    'NombreReceptor': self.partner_id.fel_nombre_sat
                }
        else:
            if (round(abs(self.amount_total_signed), 2) >= 2500) and (self.partner_id.vat == 'CF'):
                if not self.partner_id.ref:
                    raise ValidationError('Para este tipo de factura debe especificar un CUI o documento de extranjero en el campo "Referencia" del cliente, en la pestaña "Venta y Compra"')


                if self.partner_id.fel_extranjero == 'No':
                    dicReceptor = {
                        'CorreoReceptor': "",
                        'IDReceptor': self.partner_id.ref,
                        'NombreReceptor': self.partner_id.fel_nombre_sat,
                        'TipoEspecial': 'CUI'
                    }
                else:
                    dicReceptor = {
                        'CorreoReceptor': "",
                        'IDReceptor': self.partner_id.ref,
                        'NombreReceptor': self.partner_id.fel_nombre_sat,
                        'TipoEspecial': 'EXT'
                    }

            else:
                if not self.partner_id.vat:
                    raise ValidationError('Para poder facturar debe especificar un Nit, o bien especificar CF')

                dicReceptor = {
                    'CorreoReceptor': "",
                    'IDReceptor': self.partner_id.vat,
                    'NombreReceptor': self.partner_id.fel_nombre_sat
                }

        dicFrase1 = {
            'CodigoEscenario': "1",
            'TipoFrase': "2"
        }

        dicFrase2 = {
            'CodigoEscenario': "1",
            'TipoFrase': "1"
        }

        GTdocumento = ET.Element("dte:GTDocumento", dicGTDocumento)
        SAT = ET.SubElement(GTdocumento, "dte:SAT", dicSAT)
        DTE = ET.SubElement(SAT, "dte:DTE", dicDTE)
        DatosEmision = ET.SubElement(DTE, "dte:DatosEmision", dicDatosEmision)
        ET.SubElement(DatosEmision, "dte:DatosGenerales", dicDatosGenerales)
        Emisor = ET.SubElement(DatosEmision, "dte:Emisor", dicEmisor)
        DireccionEmisor = ET.SubElement(Emisor, "dte:DireccionEmisor")

        # ET.SubElement(DireccionEmisor, "dte:Direccion").text = "0 Av. A 9-24 zona 9"
        # ET.SubElement(DireccionEmisor, "dte:CodigoPostal").text = "01001"
        # ET.SubElement(DireccionEmisor, "dte:Municipio").text = "Guatemala"
        # ET.SubElement(DireccionEmisor, "dte:Departamento").text = "Guatemala"

        ET.SubElement(DireccionEmisor, "dte:Direccion").text = self.env.company.fel_direccion
        ET.SubElement(DireccionEmisor, "dte:CodigoPostal").text = self.env.company.fel_codigo_postal
        ET.SubElement(DireccionEmisor, "dte:Municipio").text = self.env.company.fel_municipio
        ET.SubElement(DireccionEmisor, "dte:Departamento").text = self.env.company.fel_departamento
        ET.SubElement(DireccionEmisor, "dte:Pais").text = "GT"

        Receptor = ET.SubElement(DatosEmision, "dte:Receptor", dicReceptor)
        DireccionReceptor = ET.SubElement(Receptor, "dte:DireccionReceptor")

        if (self.partner_id.street):
            ET.SubElement(DireccionReceptor, "dte:Direccion").text = self.partner_id.street
        else:
            ET.SubElement(DireccionReceptor, "dte:Direccion").text = "Ciudad"

        if (self.partner_id.zip):
            ET.SubElement(DireccionReceptor, "dte:CodigoPostal").text = self.partner_id.zip
        else:
            ET.SubElement(DireccionReceptor, "dte:CodigoPostal").text = "0001"

        if (self.partner_id.street2):
            ET.SubElement(DireccionReceptor, "dte:Municipio").text = self.partner_id.street2
        else:
            ET.SubElement(DireccionReceptor, "dte:Municipio").text = "ND"

        if (self.partner_id.state_id):
            ET.SubElement(DireccionReceptor, "dte:Departamento").text = self.partner_id.state_id
        else:
            ET.SubElement(DireccionReceptor, "dte:Departamento").text = "Guatemala"

        ET.SubElement(DireccionReceptor, "dte:Pais").text = "GT"

        # Aqui empieza frases que funcionan
        # if (tipo == 'FACT'):
        #     Frases = ET.SubElement(DatosEmision, "dte:Frases")
        #     for frase in self.env.company.fel_frases:
        #         dicFrase = {
        #             'CodigoEscenario': frase.fel_frases_codigo_escenario,
        #             'TipoFrase': frase.fel_frases_tipo_frase
        #         }
        #         ET.SubElement(Frases, "dte:Frase", dicFrase)
        # Aqui termina frases que funcionan

        # Segundas frases que funcionan
        #
        # Iva = round(self.amount_tax_signed, 2)
        # if (tipo != 'NCRE') and (tipo != 'NDEB'):
        #     Frases = ET.SubElement(DatosEmision, "dte:Frases")
        #     for frase in self.env.company.fel_frases:
        #         if ((frase.fel_frases_codigo_escenario == '1')
        #         or  ((Iva == 0) and (frase.fel_frases_codigo_escenario == '13'))):
        #             dicFrase = {
        #                 'CodigoEscenario': frase.fel_frases_codigo_escenario,
        #                 'TipoFrase': frase.fel_frases_tipo_frase
        #             }
        #
        #             if frase.fel_frases_tipos.count(tipo) == 1:
        #                 ET.SubElement(Frases, "dte:Frase", dicFrase)
        #
        #
        # Aqui terminan frases que funcionan 2

        if self.journal_id.fel_frases:
            Frases = ET.SubElement(DatosEmision, "dte:Frases")
            for frase in self.journal_id.fel_frases:
                dicFrase = {
                            'CodigoEscenario': frase.fel_frases_codigo_escenario,
                            'TipoFrase': frase.fel_frases_tipo_frase
                           }
                ET.SubElement(Frases, "dte:Frase", dicFrase)


        # if (tipo == 'FACT'):
        #     Frases = ET.SubElement(DatosEmision, "dte:Frases")
        #     ET.SubElement(Frases, "dte:Frase", dicFrase2)
        #     # ET.SubElement(Frases, "dte:Frase", dicFrase1)

        Items = ET.SubElement(DatosEmision, "dte:Items")

        detallesFactura = self.invoice_line_ids

        linea = 1

        for detalleFactura in detallesFactura:
            if detalleFactura.product_id.type == "service":
                dicItem = {
                    'BienOServicio': "S",
                    'NumeroLinea': str(linea),
                }
            else:
                dicItem = {
                    'BienOServicio': "B",
                    'NumeroLinea': str(linea),
                }

            linea += 1

            Item = ET.SubElement(Items, "dte:Item", dicItem)

            cantidad = str(abs(detalleFactura.quantity))
            preciounitario = str(abs(round(detalleFactura.price_unit,2)))
            precio = str(abs(round((detalleFactura.price_unit*detalleFactura.quantity),2)))
            descuento = str(abs(round(round((detalleFactura.price_unit*detalleFactura.quantity),2)-detalleFactura.price_total,2)))

            ET.SubElement(Item, "dte:Cantidad").text = cantidad
            ET.SubElement(Item, "dte:UnidadMedida").text = "UND"
            # ET.SubElement(Item, "dte:Descripcion").text = detalleFactura.product_id.name

            if detalleFactura.product_id.display_name != detalleFactura.name:
                descripcion_producto = detalleFactura.name
                if self.env.company.fel_sep_codigo == 'S' and detalleFactura.product_id.default_code:
                    descripcion_producto = detalleFactura.product_id.default_code + '|' + descripcion_producto
            else:
                if self.env.company.fel_codigo_imp == 'N':
                    descripcion_producto = detalleFactura.product_id.name
                    if self.env.company.fel_sep_codigo == 'S' and detalleFactura.product_id.default_code:
                        descripcion_producto = detalleFactura.product_id.default_code + '|' + descripcion_producto
                else:
                    descripcion_producto = detalleFactura.product_id.name + ' ' + detalleFactura.product_id.default_code

            # producto_sintres = detalleFactura.product_id.name.replace('   ', ' ')
            # producto_sintres = descripcion_producto.replace('   ', ' ')
            # producto_sindos = producto_sintres.replace('  ', ' ')
            # producto = producto_sindos.strip()

            ET.SubElement(Item, "dte:Descripcion").text = descripcion_producto
            ET.SubElement(Item, "dte:PrecioUnitario").text = preciounitario
            ET.SubElement(Item, "dte:Precio").text = precio
            ET.SubElement(Item, "dte:Descuento").text = descuento

            Impuestos = ET.SubElement(Item, "dte:Impuestos")
            Impuesto = ET.SubElement(Impuestos, "dte:Impuesto")

            gravable = round(detalleFactura.price_subtotal,2)
            montogravable = str(abs(round(detalleFactura.price_subtotal,2)))
            ivauni = abs(round(detalleFactura.price_total - detalleFactura.price_subtotal, 2))
            montoimpuesto = str(ivauni)
            total = str(abs(round(detalleFactura.price_total,2)))

            ET.SubElement(Impuesto, "dte:NombreCorto").text = "IVA"
            if (ivauni == 0) and (gravable > 0):
                ET.SubElement(Impuesto, "dte:CodigoUnidadGravable").text = "2"
            else:
                ET.SubElement(Impuesto, "dte:CodigoUnidadGravable").text = "1"
            ET.SubElement(Impuesto, "dte:MontoGravable").text = montogravable
            ET.SubElement(Impuesto, "dte:MontoImpuesto").text = montoimpuesto

            ET.SubElement(Item, "dte:Total").text = total

        Totales = ET.SubElement(DatosEmision, "dte:Totales")
        TotalImpuestos = ET.SubElement(Totales, "dte:TotalImpuestos")

        dicTotalImpuesto = {
            'NombreCorto': "IVA",
            'TotalMontoImpuesto': str(abs(round(self.amount_tax_signed, 2)))
        }

        ET.SubElement(TotalImpuestos, "dte:TotalImpuesto", dicTotalImpuesto)
        ET.SubElement(Totales, "dte:GranTotal").text = str(abs(round(self.amount_total_signed, 2)))

        if (tipo == 'NCRE') or (tipo == 'NDEB'):
            Complementos = ET.SubElement(DatosEmision, "dte:Complementos")

            diComplemento = {
                'IDComplemento': "TEXT",
                'NombreComplemento': "TEXT",
                'URIComplemento': "TEXT",
            }

            Complemento = ET.SubElement(Complementos, "dte:Complemento", diComplemento)

            dicNota = {
                'xmlns:cno': "http://www.sat.gob.gt/face2/ComplementoReferenciaNota/0.1.0",
                'FechaEmisionDocumentoOrigen': str(self.fel_fecha),
                'MotivoAjuste': "Ajustes/Modificaciones",
                'NumeroAutorizacionDocumentoOrigen' : self.fel_uuid,
                'NumeroDocumentoOrigen' : self.fel_numero,
                'SerieDocumentoOrigen' : self.fel_serie,
                'Version' : "0.0",
                'xsi:schemaLocation' : "http://www.sat.gob.gt/face2/ComplementoReferenciaNota/0.1.0"
            }

            ET.SubElement(Complemento, "cno:ReferenciasNota", dicNota)

        if (tipo == 'FESP'):
            Complementos = ET.SubElement(DatosEmision, "dte:Complementos")

            diComplemento = {
                'IDComplemento': "Especial",
                'NombreComplemento': "Especial",
                'URIComplemento': "http://www.sat.gob.gt/fel/especial.xsd",
            }

            Complemento = ET.SubElement(Complementos, "dte:Complemento", diComplemento)

            dicEsp = {
                'xmlns:cfe': "http://www.sat.gob.gt/face2/ComplementoFacturaEspecial/0.1.0",
                'Version' : "1",
                'xsi:schemaLocation' : "http://www.sat.gob.gt/face2/ComplementoFacturaEspecial/0.1.0"
            }

            FacturaEspecial = ET.SubElement(Complemento, "cfe:RetencionesFacturaEspecial", dicEsp)

            RetencionISR = round((self.amount_total_signed - self.amount_tax_signed) * (self.journal_id.fel_retencion_isr/100), 2)
            RetencionIVA = round(self.amount_tax_signed, 2)
            ET.SubElement(FacturaEspecial, "cfe:RetencionISR").text = str(abs(RetencionISR))
            ET.SubElement(FacturaEspecial, "cfe:RetencionIVA").text = str(abs(RetencionIVA))
            ET.SubElement(FacturaEspecial, "cfe:TotalMenosRetenciones").text = str(abs(round(self.amount_total_signed - RetencionIVA - RetencionISR, 2)))


        if (tipo == 'FCAM'):
            Complementos = ET.SubElement(DatosEmision, "dte:Complementos")

            diComplemento = {
                'IDComplemento': "Cambiaria",
                'NombreComplemento': "Cambiaria",
                'URIComplemento': "http://www.sat.gob.gt/fel/cambiaria.xsd",
            }

            Complemento = ET.SubElement(Complementos, "dte:Complemento", diComplemento)

            dicCamb = {
                'xmlns:cfc': "http://www.sat.gob.gt/dte/fel/CompCambiaria/0.1.0",
                'Version' : "1",
                'xsi:schemaLocation' : "http://www.sat.gob.gt/dte/fel/CompCambiaria/0.1.0"
            }

            FacturaCambiaria = ET.SubElement(Complemento, "cfc:AbonosFacturaCambiaria", dicCamb)

            Abono = ET.SubElement(FacturaCambiaria, "cfc:Abono")

            fechapago = str(self.invoice_date_due)

            ET.SubElement(Abono, "cfc:NumeroAbono").text = "1"
            ET.SubElement(Abono, "cfc:FechaVencimiento").text = fechapago
            ET.SubElement(Abono, "cfc:MontoAbono").text = str(abs(round(self.amount_total_signed, 2)))


        if (self.name == "/"):
            try:
                siguiente =  str(int(self.highest_name[13:17])+1)
                formateado = siguiente.zfill(4)
                referencia = self.highest_name[0:13]+formateado
            except ValueError:
                referencia = "Interno"+str(random.randint(0, 100000))
        else:
            referencia = self.name

        Adenda = ET.SubElement(SAT, "dte:Adenda")
        ET.SubElement(Adenda, "Referencia").text = referencia
        ET.SubElement(Adenda, "Vendedor").text = self.invoice_user_id.name

        return GTdocumento

    def firmafeldospasos(self,data):
        encoded = base64.encodebytes(ET.tostring(data)).decode("utf-8")

        urlfirma = "https://signer-emisores.feel.com.gt/sign_solicitud_firmas/firma_xml"

        headersfirma = {
            'Content-Type': "application/json"
        }

        bodyfirma = {
            'llave' : "8f898eb40aff0e4d060380004523b5ce",
            'archivo' : encoded,
            'codigo' : self.name,
            'alias' : "2459413K",
            'es_anulacion' : "N"
        }

        responsefirma = requests.post(urlfirma, json=bodyfirma, headers=headersfirma)

        urlcertificado = "https://certificador.feel.com.gt/fel/certificacion/v2/dte/"

        headerscertificado = {
            'usuario': "2459413K",
            'llave': "46155CE198281D56C1F479082C6946C7",
            'Identificador': self.name,
            'Content-Type': "application/json"
        }

        bodycertificado = {
            'nit_emisor' : "2459413K",
            'correo_copia' : "wapaiz@gmail.com",
            'xml_dte' : json.loads(responsefirma.text)['archivo']
        }

        responsecertificado = requests.post(urlcertificado, json=bodycertificado, headers=headerscertificado)

        response = {
            "resultado": False,
            "descripcion_errores": "Error generado para pruebas",
            "uuid": "GENERADO-PARA-PRUEBAS",
            "serie": "SERIE-PRUEBAS",
            "numero": 12345678,
            "descripcion_errores": [{
                "mensaje_error": "Error generado para pruebas"
                    }]
        }

        return json.loads(responsecertificado.text)
        # return response


    def firmafel(self,data):

        url = self.env.company.fel_url_firma

        response_pru = {
            "resultado": True,
            "descripcion_errores": "Generado para pruebas",
            "uuid": "GENERADO-PARA-PRUEBAS",
            "serie": "SERIE-PRUEBAS",
            "numero": 12345678,
            "descripcion_errores": [{
                "mensaje_error": "Generado para pruebas"
                    }]
        }

        headers = {
            'UsuarioFirma': self.env.company.fel_UsuarioFirma,
            'LlaveFirma': self.env.company.fel_LlaveFirma,
            'UsuarioApi': self.env.company.fel_UsuarioApi,
            'LlaveApi': self.env.company.fel_LlaveApi,
            'Identificador': data[0][1][0].text,
        }

        if self.env.company.fel_service == "S":

            # xml_data = ET.tostring(data, encoding="utf-8", xml_declaration=True)
            buffer = io.BytesIO()
            tree = ET.ElementTree(data)
            tree.write(buffer, encoding="utf-8", xml_declaration=True)
            xml_data = buffer.getvalue().decode("utf-8")
            
            response = requests.post(url, data=xml_data, headers=headers)

            return json.loads(response.text)
        else:
            return response_pru

    def genxmlanulacion(self):
        dicGTAnulacionDocumento = {
            'xmlns:ds': "http://www.w3.org/2000/09/xmldsig#",
            'xmlns:dte': "http://www.sat.gob.gt/dte/fel/0.1.0",
            'xmlns:n1' : "http://www.altova.com/samplexml/other-namespace",
            'xmlns:xsi': "http://www.w3.org/2001/XMLSchema-instance",
            'Version': "0.1",
            'xsi:schemaLocation': "http://www.sat.gob.gt/dte/fel/0.1.0"
        }

        dicAnulacionDTE = {
            'ID': "DatosCertificados"
        }

        fechafel = str(self.date)+"T"+str(self.create_date.strftime("%H:%M:%S"))+"-06:00"
        hoy = datetime.today()
        fechaanulacion = str(hoy.date())+"T"+str(hoy.strftime("%H:%M:%S"))+"-06:00"

        if (round(self.amount_total_signed, 2) > 2500) and (self.partner_id.vat == 'CF'):
            dicDatosGenerales = {
                "FechaEmisionDocumentoAnular" : fechafel,
                "FechaHoraAnulacion" : fechaanulacion,
                "ID" : "DatosAnulacion",
                "IDReceptor" : self.partner_id.ref,
                "MotivoAnulacion" : "Anulacion de documento FEL",
                "NITEmisor" : self.env.company.fel_nit_emisor,
                "NumeroDocumentoAAnular" : self.fel_uuid
            }
        else:
            dicDatosGenerales = {
                "FechaEmisionDocumentoAnular" : fechafel,
                "FechaHoraAnulacion" : fechaanulacion,
                "ID" : "DatosAnulacion",
                "IDReceptor" : self.partner_id.vat,
                "MotivoAnulacion" : "Anulacion de documento FEL",
                "NITEmisor" : self.env.company.fel_nit_emisor,
                "NumeroDocumentoAAnular" : self.fel_uuid
            }

        GTAnulaciondocumento = ET.Element("dte:GTAnulacionDocumento", dicGTAnulacionDocumento)
        SAT = ET.SubElement(GTAnulaciondocumento, "dte:SAT")
        AnulacionDTE = ET.SubElement(SAT, "dte:AnulacionDTE", dicAnulacionDTE)
        ET.SubElement(AnulacionDTE, "dte:DatosGenerales", dicDatosGenerales)

        return GTAnulaciondocumento

    def firmaanulafel(self,data):

        url = self.env.company.fel_url_firma

        headers = {
            'UsuarioFirma': self.env.company.fel_UsuarioFirma,
            'LlaveFirma': self.env.company.fel_LlaveFirma,
            'UsuarioApi': self.env.company.fel_UsuarioApi,
            'LlaveApi': self.env.company.fel_LlaveApi,
            'Identificador': self.name,
        }

        # response = requests.post(url, data=ET.tostring(data), headers=headers)

        xml_data = ET.tostring(data, encoding="utf-8", xml_declaration=True)
        response = requests.post(url, data=xml_data, headers=headers)

        return json.loads(response.text)

    def generaFel(self):
        if (self.move_type == "out_invoice") or (self.move_type == "in_invoice"):

            fel_Xml = controllerfel.genxml(self,self.journal_id.fel_tipo_fel)

            if self.env.company.fel_entorno == "D":
                ET.ElementTree(fel_Xml).write("/home/iitadmin/Documentos/Odoo/odoo-14.0/fel/pararevisar.xml",encoding="unicode")
            else:
                ET.ElementTree(fel_Xml).write("/opt/odoo/fel/pararevisar.xml",encoding="unicode")

            data = controllerfel.firmafel(self,fel_Xml)



            if not data['resultado']:
                if self.env.company.fel_entorno == "D":
                    ruta = "/home/iitadmin/Documentos/Odoo/odoo-14.0/fel/error.json"
                else:
                    ruta = "/opt/odoo/fel/error.json"

                with open(ruta, 'w') as fp:
                    json.dump(data, fp)

                errores = data['descripcion_errores']
                raise ValidationError(errores[0]['mensaje_error'])

            if self.env.company.fel_entorno == "D":
                ET.ElementTree(fel_Xml).write("/home/iitadmin/Documentos/Odoo/odoo-14.0/fel/" + data['uuid'] + ".xml", encoding="unicode")
            else:
                ET.ElementTree(fel_Xml).write("/opt/odoo/fel/" + data['uuid'] + ".xml",encoding="unicode")

            self.fel_uuid = data['uuid']
            self.fel_serie = data['serie']
            self.fel_numero = data['numero']
            self.fel_certificado = 'Certificado'
            self.fel_fecha = self.create_date

        if (self.move_type == "out_refund"):

            fel_Xml = controllerfel.genxml(self,self.journal_id.fel_tipo_fel)

            data = controllerfel.firmafel(self,fel_Xml)

            if not data['resultado']:

                if self.env.company.fel_entorno == "D":
                    ruta = "/home/iitadmin/Documentos/Odoo/odoo-14.0/fel/error.json"
                else:
                    ruta = "/opt/odoo/fel/error.json"

                with open(ruta, 'w') as fp:
                    json.dump(data, fp)

                errores = data['descripcion_errores']
                raise ValidationError(errores[0]['mensaje_error'])

            if self.env.company.fel_entorno == "D":
                ET.ElementTree(fel_Xml).write("/home/iitadmin/Documentos/Odoo/odoo-14.0/fel/" + data['uuid'] + ".xml", encoding="unicode")
            else:
                ET.ElementTree(fel_Xml).write("/opt/odoo/fel/" + data['uuid'] + ".xml",encoding="unicode")

            self.fel_uuid = data['uuid']
            self.fel_serie = data['serie']
            self.fel_numero = data['numero']
            self.fel_certificado = 'Certificado'
            self.fel_fecha = self.create_date

    def anulafel(self):
        if (self.fel_certificado == 'Certificado'):

            fel_AnulaXml = controllerfel.genxmlanulacion(self)

            if self.env.company.fel_entorno == "D":
                ET.ElementTree(fel_AnulaXml).write("/home/iitadmin/Documentos/Odoo/odoo-14.0/fel/pararevisar_anula.xml",encoding="unicode")
            else:
                ET.ElementTree(fel_AnulaXml).write("/opt/odoo/fel/pararevisar_anula.xml",encoding="unicode")

            anula_fel = controllerfel.firmaanulafel(self,fel_AnulaXml)

            if not anula_fel['resultado']:

                if self.env.company.fel_entorno == "D":
                    ruta = "/home/iitadmin/Documentos/Odoo/odoo-14.0/fel/error.json"
                else:
                    ruta = "/opt/odoo/fel/error.json"

                with open(ruta, 'w') as fp:
                    json.dump(anula_fel, fp)

                errores = anula_fel['descripcion_errores']
                raise ValidationError(errores[0]['mensaje_error'])

            if self.env.company.fel_entorno == "D":
                ET.ElementTree(fel_AnulaXml).write("/home/iitadmin/Documentos/Odoo/odoo-14.0/fel/" + self.fel_uuid + "_anula.xml", encoding="unicode")
            else:
                ET.ElementTree(fel_AnulaXml).write("/opt/odoo/fel/" + self.fel_uuid + "_anula.xml",encoding="unicode")

