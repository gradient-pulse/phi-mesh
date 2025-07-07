
import h5py, numpy as np, argparse

def detect_nt(g, sigma=1.5):
    dt = 1.0
    dZ = np.gradient(g, dt)
    thr = sigma * dZ.std()
    flips = np.where((np.sign(dZ[:-1]) != np.sign(dZ[1:])) &
                     (np.abs(dZ[1:]) > thr))[0]
    return flips

if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Detect Narrative Ticks from G(t)")
    p.add_argument("file", help="HDF5 file with dataset 'G_t'")
    p.add_argument("--sigma", type=float, default=1.5, help="threshold multiplier")
    args = p.parse_args()

    with h5py.File(args.file, "r") as f:
        g = f["G_t"][...]
    nts = detect_nt(g, args.sigma)
    np.savetxt("nt_times.txt", nts)
    print(f"Found {len(nts)} NTs saved to nt_times.txt")
