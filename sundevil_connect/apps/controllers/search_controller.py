from apps.core.models import Club, Event

class SearchController:
    
    def search_clubs(self, filter_payload: dict) -> list[Club]:
        clubs = Club.objects.filter(is_active=True)

        if 'query' in filter_payload and filter_payload['query']:
            clubs = clubs.filter(name__icontains=filter_payload['query'])

        clubs_list = list(clubs)

        if 'category' in filter_payload and filter_payload['category']:
            category = filter_payload['category']
            clubs_list = [c for c in clubs_list if c.categories and category in c.categories]

        return clubs_list
    
    def search_events(self, filter_payload: dict) -> list[Event]:
        events = Event.objects.select_related('club').filter(status='UPCOMING')

        if 'query' in filter_payload and filter_payload['query']:
            events = events.filter(title__icontains=filter_payload['query'])

        if 'is_free' in filter_payload:
            events = events.filter(is_free=filter_payload['is_free'])

        if 'club_id' in filter_payload:
            events = events.filter(club_id=filter_payload['club_id'])

        if 'location' in filter_payload and filter_payload['location']:
            events = events.filter(location__icontains=filter_payload['location'])

        sort_by = filter_payload.get('sort', 'date_asc')
        if sort_by == 'date_asc':
            events = events.order_by('start_time')
        elif sort_by == 'date_desc':
            events = events.order_by('-start_time')
        elif sort_by == 'popularity':
            events = events.order_by('-registered_count')
        elif sort_by == 'name':
            events = events.order_by('title')
        else:
            events = events.order_by('start_time')

        events_list = list(events)

        if 'category' in filter_payload and filter_payload['category']:
            category = filter_payload['category']
            events_list = [e for e in events_list if e.categories and category in e.categories]

        return events_list