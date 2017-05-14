from tqdm import tqdm
from concurrent.futures import ProcessPoolExecutor, as_completed


def run_parallel(arr, fn, n_jobs=8, use_kwargs=False):
    if n_jobs==1:
        return [fn(**a) if use_kwargs else fn(a) for a in tqdm(arr)]
    #Assemble the workers
    with ProcessPoolExecutor(max_workers=n_jobs) as pool:
        #Pass the elements of array into function
        if use_kwargs:
            futures = [pool.submit(fn, **a) for a in arr]
        else:
            futures = [pool.submit(fn, a) for a in arr]
        kwargs = {
            'total': len(futures),
            'unit': 'it',
            'unit_scale': True,
            'leave': True
        }
        #Print out the progress as tasks complete
        for f in tqdm(as_completed(futures), **kwargs):
            pass
    out = []
    #Get the results from the futures.
    for i, future in tqdm(enumerate(futures)):
        try:
            out.append(future.result())
        except Exception as e:
            out.append(e)
    return out
