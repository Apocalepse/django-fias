# -*- coding: utf-8 -*-
import json
from django.utils.text import force_text
from fias.models import AddrObj, SocrBase
from django.http import Http404, JsonResponse
from django.views.generic.base import View
from django.views.generic import ListView


EMPTY_RESULT = 'nil', False, ()


class SuggestAddressViewStepByStep(View):

    def get(self, request, *args, **kwargs):
        filter_params = None
        term = request.GET.get('term', None)
        if not term:
            raise Http404

        level = 0
        result_parts = []
        result = []
        parts = term.split(',')

        parts_len = len(parts)

        """
            Проверяем иерархию для всех объектов перед последней запятой
        """
        if parts_len > 1:

            for part in parts[:-1]:
                socr_term, obj_term = part.strip().split(' ', 1)
                socr_term = socr_term.rstrip('.')
                part_qs = AddrObj.objects.filter(shortname__iexact=socr_term, formalname__iexact=obj_term)

                if level > 0:
                    part_qs = part_qs.filter(parentguid=result_parts[level-1].aoguid)

                if len(part_qs) == 1:
                    level += 1
                    result_parts.append(part_qs[0])
                elif len(part_qs) > 1:
                    raise Exception('Lots of options???')
                else:
                    return EMPTY_RESULT

        """
            Строку после последней запятой проверяем более тщательно
        """

        last = parts[-1].lstrip()
        last_len = len(last)

        # Это сокращение и начало названия объекта?
        if ' ' in last:
            socr_term, obj_term = last.split(' ', 1)
            socr_term = socr_term.rstrip('.')

            sqs = SocrBase.objects.filter(scname__icontains=socr_term).distinct()

            if level > 0:
                sqs = sqs.filter(level__gt=result_parts[-1].aolevel)

            sqs_len = len(sqs)
            obj_term = obj_term.strip()

            if sqs_len > 1:
                levels = []
                socrs = []
                for s in sqs:
                    levels.append(s.level)
                    socrs.append(s.scname)

                filter_params = dict(
                    aolevel__in=set(levels),
                    shortname__in=set(socrs),
                )
            elif sqs_len == 1:
                filter_params = dict(
                    aolevel=sqs[0].level,
                    shortname=sqs[0].scname,
                )
            else:
                pass

            if filter_params:
                if obj_term:
                    filter_params.update(formalname__icontains=obj_term)
                if level > 0:
                    filter_params.update(parentguid=result_parts[-1].aoguid, aolevel__gt=result_parts[-1].aolevel)

        # Это только сокращение?
        elif last_len < 10:
            sqs = SocrBase.objects.filter(scname__icontains=last)

            if level > 0:
                sqs = sqs.filter(level__gt=result_parts[-1].aolevel)

            sqs_len = len(sqs)
            if sqs_len:
                result = ((None, s.scname) for s in sqs)
            else:
                filter_params = dict(
                    formalname__icontains=last
                )

                if level > 0:
                    filter_params.update(parentguid=result_parts[-1].aoguid, aolevel__gt=result_parts[-1].aolevel)

        prefix = ', '.join((r.get_formal_name() for r in result_parts)) if result_parts else ''

        if result:
            if prefix:
                return JsonResponse({'err': 'nil', 'results': ((k, '{0}, {1}'.format(prefix, v)) for k, v in result)})

            return JsonResponse({'err': 'nil', 'results': result})

        if filter_params is not None:
            result = AddrObj.objects.order_by('aolevel').filter(**filter_params)[:10]

            if prefix:
                return JsonResponse({
                    'err': 'nil',
                    'results': ((force_text(l.pk), '{0}, {1}'.format(prefix, l), {'level': l.aolevel}) for l in result)
                })
            else:
                return JsonResponse({
                    'err': 'nil',
                    'results': ((force_text(l.pk), l.full_name(5, True), {'level': l.aolevel}) for l in result)
                })

        return EMPTY_RESULT


class SuggestBySphinx(View):

    def get(self, request, *args, **kwargs):
        from fias.sphinxit import search
        term = request.GET.get('term', None)
        if not term:
            raise Http404

        query = search().match(term + '*').options(field_weights={'formalname': 100, 'fullname': 80}).limit(0, 50)

        # Hack to bypass bug in sphixit. https://github.com/semirook/sphinxit/issues/16
        
        # TODO не смог разобраться, у меня регалось на последний weight()
        # query._nodes.OrderBy.orderings = [u'item_weight DESC', u'weight() DESC']
        query._nodes.OrderBy.orderings = [u'item_weight DESC']

        result = query.ask()

        items = result['result']['items']

        if len(items):
            results = [{'id': l['aoguid'], 'text': l['fullname']} for l in items]
            return JsonResponse({
                'err': 'nil',
                'results': results
            })

        return EMPTY_RESULT


class GetAreasListView(ListView):

    def get(self, request, *args, **kwargs):
        if request.method == 'GET':
            guid = request.GET.get('guid', None)
            if guid is None:
                return self.render_to_response(self._results_to_context(('missing guid', False, [], )))
            if not guid:
                return self.render_to_response(self._results_to_context(('nil', False, [], )))

        else:
            return self.render_to_response(self._results_to_context(('not a get request', False, [], )))

        try:
            address = AddrObj.objects.get(pk=guid)
        except AddrObj.DoesNotExist:
            return self.render_to_response(self._results_to_context(('wrong guid', False, [], )))

        city = self._get_city_obj(address)

        if city is None:
            return self.render_to_response(self._results_to_context(('nil', False, [], )))

        areas = AddrObj.objects.filter(parentguid=city.pk, shortname='р-н')

        if areas:
            return self.render_to_response(self._results_to_context((
                'nil',
                False,
                ((force_text(a.pk), force_text(a)) for a in areas), ))
            )

        return self.render_to_response(self._results_to_context(('nil', False, [], )))

    def _get_city_obj(self, obj):
        if obj.shortname != 'г' and obj.aolevel > 1:
            parent = AddrObj.objects.get(pk=obj.parentguid)
            return self._get_city_obj(parent)
        elif obj.shortname == 'г':
            return obj
        else:
            return None
