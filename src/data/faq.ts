/**
 * Preguntas frecuentes — respuestas genéricas y veraces; sin plazos ni marcas inventadas.
 */
import { company } from './company';
import { contact } from './contact';

export interface FaqItem {
  id: string;
  question: string;
  answer: string;
}

export const faqItems: FaqItem[] = [
  {
    id: '1',
    question: '¿Cómo solicito una cotización?',
    answer:
      'Escríbanos a ' +
      contact.email +
      ' o por WhatsApp al ' +
      contact.phoneDisplay +
      '. Indique categoría (alimentos, control de calidad o laboratorio clínico), aplicación o equipo de referencia si la tiene, y su institución o ciudad. Con eso podemos orientar la siguiente respuesta.',
  },
  {
    id: '2',
    question: '¿Qué tipo de clientes atienden?',
    answer:
      company.audience.join(', ') +
      '. Atención en todo ' +
      company.geography +
      '.',
  },
  {
    id: '3',
    question: '¿Tienen catálogos o fichas técnicas?',
    answer: company.catalogNote,
  },
  {
    id: '4',
    question: '¿Cómo los contacto y en qué horario?',
    answer:
      'Correo ' +
      contact.email +
      ', teléfono y WhatsApp ' +
      contact.phoneDisplay +
      '. Ubicación: ' +
      contact.locationPublic +
      '. Horario de referencia: lunes a viernes ' +
      contact.hours +
      ' (confirmar por el canal que use).',
  },
];
