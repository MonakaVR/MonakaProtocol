"""Explicit protocol-only golden scenarios; not backend or hardware proof."""
import copy,json,pathlib
R=pathlib.Path(__file__).resolve().parents[1];F=R/'fixtures/p1';F.mkdir(exist_ok=True)
base=json.loads((R/'fixtures/v2/observation.json').read_text())
tokens=['position','orientation','linear_velocity','angular_velocity','linear_acceleration','battery_fraction','charging']
index=[]
def put(name,m,states=None,error=None,**extra):
 (F/(name+'.json')).write_text(json.dumps(m,indent=2)+'\n',encoding='utf-8')
 index.append(dict(file=name+'.json',error=error,states=states,**extra))
def obs():
 m=copy.deepcopy(base);m.update(capabilities=['position','orientation','linear_velocity'],sequence='1',timestamp_ns='100',sent_at_ns='120',battery=None)
 m['linear_velocity']={'value':[0.,0.,0.],'frame':'space','evidence':'measured'}
 m['angular_velocity']=m['linear_acceleration']=None
 return m
m=obs();put('pico-like-supported-valid',m,dict(position='VALID',orientation='VALID',linear_velocity='VALID'))
m=obs();m.update(validity=dict(position=False,orientation=False),modality='none',tracking_state='lost',orientation_evidence='none',linear_velocity=None,sequence='2',timestamp_ns='130',sent_at_ns='150');put('pico-like-position-loss',m,dict(position='INVALID',orientation='INVALID',linear_velocity='ABSENT'))
put('pico-like-full-loss-stale',m,dict(position='INVALID',orientation='INVALID',linear_velocity='ABSENT'),diagnostic='Stale/loss encoded as NONE; actual stale-age enforcement belongs to consumer, never capability deletion')
m=obs();m['linear_velocity']=None;put('supported-optional-absent',m,dict(position='VALID',orientation='VALID',linear_velocity='ABSENT'))
m=obs();m.update(capabilities=['orientation'],validity=dict(position=False,orientation=True),modality='rotation_only',tracking_state='degraded',linear_velocity=None);put('unsupported-position-diagnostic',m,dict(orientation='VALID'))
m=obs();m.update(capabilities=[],validity=dict(position=False,orientation=False),modality='none',tracking_state='lost',orientation_evidence='none',linear_velocity=None);put('empty-no-support',m,{})
m=obs();m['capabilities']=['linear_velocity','orientation','position'];put('set-order-reversed',m,dict(position='VALID',orientation='VALID',linear_velocity='VALID'))
m=obs();m['capabilities'].append('raw_gyro');put('unknown-capability',m,error='UnsupportedValue')
m=obs();m['capabilities'].append('position');put('duplicate-capability',m,error='InconsistentValidity')
m=obs();m['capabilities']=['position','orientation'];put('unsupported-derivative',m,error='InconsistentValidity')
m=obs();m['capabilities']=['orientation','linear_velocity'];put('unsupported-valid-position',m,error='InconsistentValidity')
m=obs();m.update(capabilities=['position','orientation','angular_velocity'],validity=dict(position=False,orientation=True),modality='rotation_only',tracking_state='degraded',linear_velocity=None,angular_velocity={'value':[0.,0.2,0.],'frame':'device','evidence':'measured'});put('synthetic-same-tracker-position-loss',m,dict(position='INVALID',orientation='VALID',angular_velocity='VALID'),synthetic=True,authenticity='PICO same-tracker IMU authenticity: NOT VERIFIED / DEFERRED')
m=obs();m.update(sequence='2',timestamp_ns='130',sent_at_ns='150',validity=dict(position=False,orientation=False),modality='none',tracking_state='lost',orientation_evidence='none',linear_velocity=None);put('admission-candidate',m,dict(position='INVALID',orientation='INVALID',linear_velocity='ABSENT'),backend_private=dict(raw_valid=True,state='CANDIDATE'))
m=obs();m.update(sequence='3',timestamp_ns='160',sent_at_ns='180');put('admission-admitted',m,dict(position='VALID',orientation='VALID',linear_velocity='VALID'),backend_private=dict(raw_valid=True,state='ADMITTED'))
m=obs();m.update(session_id='aaaaaaaa-aaaa-4aaa-aaaa-aaaaaaaaaaaa',clock_id='bbbbbbbb-bbbb-4bbb-bbbb-bbbbbbbbbbbb',sequence='0');put('session-restart',m,dict(position='VALID',orientation='VALID',linear_velocity='VALID'))
m=obs();m.update(source_id='another-source');put('same-device-other-source',m,dict(position='VALID',orientation='VALID',linear_velocity='VALID'))
state={k:v for k,v in obs().items() if k in ['protocol','version','source_id','session_id','clock_id','sequence','timestamp_ns','sent_at_ns','timestamp_kind','device_id','coordinate_space','capabilities','modality','battery']}
state.update(type='device_state',presence='present',tracking_state='tracked',capabilities=tokens,battery=dict(fraction=0.0,charging=False,timestamp_ns='100'));put('metadata-not-pose-validity',state,{**{t:'ABSENT' for t in tokens[:5]},'battery_fraction':'VALID','charging':'VALID'})
mtp=json.loads((R/'fixtures/v2/mtp.json').read_text()) if (R/'fixtures/v2/mtp.json').exists() else next(r['decoded'] for r in json.loads((R/'fixtures/v2/index.json').read_text()) if (r.get('decoded') or {}).get('protocol')=='monaka.tracking' and (r.get('decoded') or {}).get('type')=='pose')
mtp=copy.deepcopy(mtp);mtp.update(capabilities=['position','orientation','linear_velocity'],sequence='1',timestamp_ns='100',sent_at_ns='120',linear_velocity=[0.,0.,0.],angular_velocity=None,linear_acceleration=None)
put('legacy-bridge-first-pose',mtp,dict(position='VALID',orientation='VALID',linear_velocity='VALID'))
m=copy.deepcopy(mtp);m.update(sequence='2',timestamp_ns='130',sent_at_ns='150',angular_velocity=[0.,0.,0.],capabilities=['position','orientation','linear_velocity','angular_velocity']);put('legacy-bridge-second-derived-pose',m,dict(position='VALID',orientation='VALID',linear_velocity='VALID',angular_velocity='VALID'))
m={k:v for k,v in mtp.items() if k in ['protocol','version','publisher_id','source_id','session_id','clock_id','sequence','timestamp_ns','sent_at_ns','timestamp_kind','tracker_id','coordinate_space','capabilities','modality','mapping_revision']}
m.update(type='tracker_state',presence='present',tracking_state='tracked',capabilities=['position','orientation'],battery=None);put('legacy-bridge-state',m,dict(position='ABSENT',orientation='ABSENT'))
m=copy.deepcopy(mtp);m['publisher_id']='publisher-B';put('same-source-tracker-other-publisher',m,dict(position='VALID',orientation='VALID',linear_velocity='VALID'))
(F/'index.json').write_text(json.dumps(index,indent=2)+'\n',encoding='utf-8')
for name,wire,decl in [('observation-contract',obs(),['position','orientation','linear_velocity']),('legacy-bridge-contract',mtp,['position','orientation','linear_velocity','angular_velocity'])]:
 ident=dict(family=wire['protocol'],publisher=wire.get('publisher_id',''),source=wire['source_id'],entity=wire.get('device_id',wire.get('tracker_id')))
 (F/(name+'.binding.json')).write_text(json.dumps(dict(identity=ident,session=wire['session_id'],declaration=decl,provenance='P1 explicit fixture provision; frozen P0 B1/B3 structural bridge profile' if name.startswith('legacy') else 'P1 explicit fixture source contract'),indent=2)+'\n',encoding='utf-8')
print('Created',len(index),'explicit protocol-only golden cases')
