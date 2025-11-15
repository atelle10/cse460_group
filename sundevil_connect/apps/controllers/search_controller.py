from apps.core.models import Club, Event

class SearchController:
    
    def search_clubs(self, filter_payload: dict) -> list[Club]:
        clubs = Club.objects.filter(is_active=True)
        
        if 'query' in filter_payload and filter_payload['query']:
            clubs = clubs.filter(name__icontains=filter_payload['query'])
        
        if 'category' in filter_payload and filter_payload['category']:
            clubs = clubs.filter(categories__contains=filter_payload['category'])
            
        return list(clubs)
    
    def search_events(self, filter_payload: dict) -> list[Event]:
        events = Event.objects.select_related('club').filter(status='UPCOMING')
        
        if 'query' in filter_payload and filter_payload['query']:
            events = events.filter(title__icontains=filter_payload['query'])
        
        if 'is_free' in filter_payload:
            events = events.filter(is_free=filter_payload['is_free'])
        
        if 'club_id' in filter_payload:
            events = events.filter(club_id=filter_payload['club_id'])
            
        return list(events)